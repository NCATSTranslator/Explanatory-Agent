#!/usr/bin/env python
# coding: utf-8

# In[1]:


import tensorflow as tf
if __name__ == "__main__":
    import modeling
    import tokenization
else:
    from . import tokenization
    from . import modeling
import pandas
import os
import collections
import csv
import numpy as np
from modConfig import bert_checkpoints_folder


# In[2]:


def create_model(bert_config, is_training, input_ids, input_mask, segment_ids, labels, num_labels, use_one_hot_embeddings):
    model = modeling.BertModel(config=bert_config, is_training=is_training, input_ids=input_ids,
                               input_mask=input_mask, token_type_ids=segment_ids, use_one_hot_embeddings=use_one_hot_embeddings)
    output_layer = model.get_pooled_output()
    hidden_size = output_layer.shape[-1].value
    output_weights = tf.get_variable("output_weights", [num_labels, hidden_size],
                                     initializer=tf.truncated_normal_initializer(stddev=0.02))
    output_bias = tf.get_variable("output_bias", [num_labels], initializer=tf.zeros_initializer())
    with tf.variable_scope("loss"):
        if is_training:
            output_layer = tf.nn.dropout(output_layer, keep_prob=0.9)
        logits = tf.matmul(output_layer, output_weights, transpose_b=True)
        logits = tf.nn.bias_add(logits, output_bias)
        probabilities = tf.nn.softmax(logits, axis=-1)
        log_probs = tf.nn.log_softmax(logits, axis=-1)
        one_hot_labels = tf.one_hot(labels, depth=num_labels, dtype=tf.float32)
        per_example_loss = -tf.reduce_sum(one_hot_labels * log_probs, axis=-1)
        loss = tf.reduce_mean(per_example_loss)
        return (loss, per_example_loss, logits, probabilities)

def model_fn_builder(bert_config, num_labels, init_checkpoint, learning_rate, 
                     num_train_steps, num_warmup_steps, use_tpu,
                     use_one_hot_embeddings):
    def model_fn(features, labels, mode, params):  # pylint: disable=unused-argument
        input_ids = features["input_ids"]
        input_mask = features["input_mask"]
        segment_ids = features["segment_ids"]
        label_ids = features["label_ids"]
        is_real_example = None
        if "is_real_example" in features:
            is_real_example = tf.cast(features["is_real_example"], dtype=tf.float32)
        else:
            is_real_example = tf.ones(tf.shape(label_ids), dtype=tf.float32)
        is_training = (mode == tf.estimator.ModeKeys.TRAIN)
    
        (total_loss, per_example_loss, logits, probabilities) = create_model(
            bert_config, is_training, input_ids, input_mask, segment_ids, label_ids,
            num_labels, use_one_hot_embeddings)

        tvars = tf.trainable_variables()
        initialized_variable_names = {}
        scaffold_fn = None
        if init_checkpoint:
            (assignment_map, initialized_variable_names) = modeling.get_assignment_map_from_checkpoint(tvars, init_checkpoint)
            if use_tpu:
                def tpu_scaffold():
                    tf.train.init_from_checkpoint(init_checkpoint, assignment_map)
                    return tf.train.Scaffold()
                scaffold_fn = tpu_scaffold
            else:
                tf.train.init_from_checkpoint(init_checkpoint, assignment_map)
                
        for var in tvars:
            init_string = ""
            if var.name in initialized_variable_names:
                init_string = ", *INIT_FROM_CKPT*"
      
        output_spec = None
        if mode == tf.estimator.ModeKeys.TRAIN:
            train_op = optimization.create_optimizer(
                total_loss, learning_rate, num_train_steps, num_warmup_steps, use_tpu)
            output_spec = tf.contrib.tpu.TPUEstimatorSpec(
                mode=mode,
                loss=total_loss,
                train_op=train_op,
                scaffold_fn=scaffold_fn)
            
        elif mode == tf.estimator.ModeKeys.EVAL:
            def metric_fn(per_example_loss, label_ids, logits, is_real_example):
                predictions = tf.argmax(logits, axis=-1, output_type=tf.int32)
                accuracy = tf.metrics.accuracy(
                    labels=label_ids, predictions=predictions, weights=is_real_example)
                loss = tf.metrics.mean(values=per_example_loss, weights=is_real_example)
                return {
                    "eval_accuracy": accuracy,
                    "eval_loss": loss,
                }
            eval_metrics = (metric_fn,[per_example_loss, label_ids, logits, is_real_example])
            output_spec = tf.contrib.tpu.TPUEstimatorSpec(
                mode=mode,
                loss=total_loss,
                eval_metrics=eval_metrics,
                scaffold_fn=scaffold_fn)
        else:
            output_spec = tf.contrib.tpu.TPUEstimatorSpec(
                mode=mode,
                predictions={"probabilities": probabilities},
                scaffold_fn=scaffold_fn)
        return output_spec
    return model_fn


# In[3]:


class InputExample(object):
    def __init__(self, guid, text_a, text_b=None, label=None):
        self.guid = guid
        self.text_a = text_a
        self.text_b = text_b
        self.label = label
    
class DataProcessor(object):
    def get_train_examples(self, data_dir):
        raise NotImplementedError()

    def get_dev_examples(self, data_dir):
        raise NotImplementedError()
        
    def get_test_examples(self, data_dir):
        raise NotImplementedError()
    
    def get_test_example(self, data_eg):
        raise NotImplementedError()
    
    def get_labels(self):
        raise NotImplementedError()
        
    @classmethod
    def _read_tsv(cls, input_file, quotechar=None):
        with tf.gfile.Open(input_file, "r") as f:
            reader = csv.reader(f, delimiter="\t", quotechar=quotechar)
            lines = []
            for line in reader:
                lines.append(line)
            return lines

class BioBERTChemprotProcessor(DataProcessor):
    def get_train_examples(self, data_dir):
        return self._create_examples(
            self._read_tsv(os.path.join(data_dir, "train.tsv")), "train")
    def get_dev_examples(self, data_dir):
        return self._create_examples(
            self._read_tsv(os.path.join(data_dir, "dev.tsv")), "dev")
    def get_test_examples(self, data_dir):
        return self._create_examples(
            self._read_tsv(os.path.join(data_dir, "test.tsv")), "test")
    
    def get_test_example(self, sentences):
        line = [['index', 'sentence', 'label']]
        # line.append(['0', data_eg])
        line += [[str(i), sentence] for i, sentence in enumerate(sentences)]
        return self._create_examples(line, "test")
    
    def get_labels(self):
        return ["cpr:3", "cpr:4", "cpr:5", "cpr:6", "cpr:9", "false"]
    
    def _create_examples(self, lines, set_type):
        examples = []
        for (i, line) in enumerate(lines):
            if set_type == "test" and i == 0:
                continue
            guid = "%s-%s" % (set_type, i)
            if set_type == "test":
                text_a = tokenization.convert_to_unicode(line[1])
                label = "false"
            else:
                text_a = tokenization.convert_to_unicode(line[0])
                label = tokenization.convert_to_unicode(line[1])
            examples.append(
                InputExample(guid=guid, text_a=text_a, text_b=None, label=label))
        return examples


# In[4]:


class InputFeatures(object):
    def __init__(self, input_ids, input_mask, segment_ids, label_id, is_real_example=True):
        self.input_ids = input_ids
        self.input_mask = input_mask
        self.segment_ids = segment_ids
        self.label_id = label_id
        self.is_real_example = is_real_example
    
class PaddingInputExample(object):
    """Fake example so the num input examples is a multiple of the batch size.
    When running eval/predict on the TPU, we need to pad the number of examples
    to be a multiple of the batch size, because the TPU requires a fixed batch
    size. The alternative is to drop the last batch, which is bad because it means
    the entire output data won't be generated.
    We use this class instead of `None` because treating `None` as padding
    battches could cause silent errors.
    """

def convert_single_example(ex_index, example, label_list, max_seq_length,
                           tokenizer):
    if isinstance(example, PaddingInputExample):
        return InputFeatures( input_ids=[0] * max_seq_length, input_mask=[0] * max_seq_length,
                             segment_ids=[0] * max_seq_length, label_id=0,is_real_example=False)
    label_map = {}
    for (i, label) in enumerate(label_list):
        label_map[label] = i
    tokens_a = tokenizer.tokenize(example.text_a)
    tokens_b = None
    if example.text_b:
        tokens_b = tokenizer.tokenize(example.text_b)
    if tokens_b:
        _truncate_seq_pair(tokens_a, tokens_b, max_seq_length - 3)
    else:
        if len(tokens_a) > max_seq_length - 2:
            tokens_a = tokens_a[0:(max_seq_length - 2)]
    tokens = []
    segment_ids = []
    tokens.append("[CLS]")
    segment_ids.append(0)
    for token in tokens_a:
        tokens.append(token)
        segment_ids.append(0)
    tokens.append("[SEP]")
    segment_ids.append(0)
    
    if tokens_b:
        for token in tokens_b:
            tokens.append(token)
            segment_ids.append(1)
        tokens.append("[SEP]")
        segment_ids.append(1)
        
    input_ids = tokenizer.convert_tokens_to_ids(tokens)
    input_mask = [1] * len(input_ids)
    
    while len(input_ids) < max_seq_length:
        input_ids.append(0)
        input_mask.append(0)
        segment_ids.append(0)
        
    assert len(input_ids) == max_seq_length
    assert len(input_mask) == max_seq_length
    assert len(segment_ids) == max_seq_length
    
    label_id = label_map[example.label]
    
    feature = InputFeatures(input_ids=input_ids, input_mask=input_mask, segment_ids=segment_ids,
                            label_id=label_id, is_real_example=True)
    return feature

def file_based_convert_examples_to_features(examples, label_list, max_seq_length, tokenizer, output_file):
    writer = tf.python_io.TFRecordWriter(output_file)
    for (ex_index, example) in enumerate(examples):
        feature = convert_single_example(ex_index, example, label_list, 
                                         max_seq_length, tokenizer)

        def create_int_feature(values):
            f = tf.train.Feature(int64_list=tf.train.Int64List(value=list(values)))
            return f
        features = collections.OrderedDict()
        features["input_ids"] = create_int_feature(feature.input_ids)
        features["input_mask"] = create_int_feature(feature.input_mask)
        features["segment_ids"] = create_int_feature(feature.segment_ids)
        features["label_ids"] = create_int_feature([feature.label_id])
        features["is_real_example"] = create_int_feature([int(feature.is_real_example)])
        tf_example = tf.train.Example(features=tf.train.Features(feature=features))
        writer.write(tf_example.SerializeToString())
    writer.close()


# In[5]:


def file_based_input_fn_builder(input_file, seq_length, is_training, drop_remainder):
    name_to_features = {
        "input_ids": tf.FixedLenFeature([seq_length], tf.int64),
        "input_mask": tf.FixedLenFeature([seq_length], tf.int64),
        "segment_ids": tf.FixedLenFeature([seq_length], tf.int64),
        "label_ids": tf.FixedLenFeature([], tf.int64),
        "is_real_example": tf.FixedLenFeature([], tf.int64),
    }
    
    def _decode_record(record, name_to_features):
        example = tf.parse_single_example(record, name_to_features)
        for name in list(example.keys()):
            t = example[name]
            if t.dtype == tf.int64:
                t = tf.to_int32(t)
            example[name] = t
        return example
    
    def input_fn(params):
        batch_size = params["batch_size"]
        d = tf.data.TFRecordDataset(input_file)
        if is_training:
            d = d.repeat()
            d = d.shuffle(buffer_size=100)
        d = d.apply(
            tf.contrib.data.map_and_batch(
                lambda record: _decode_record(record, name_to_features),
                batch_size=batch_size,
                drop_remainder=drop_remainder))
        return d
    return input_fn


# In[6]:

def relationship_classification(sentences):
    if __name__ == "__main__":
        biobert_re_finetuned_vocab = os.path.join(os.path.join(os.getcwd(), "re_outputs"), "vocab.txt")
        biobert_re_finetuned_config = os.path.join(os.path.join(os.getcwd(), "re_outputs"), "bert_config.json")
        biobert_re_finetuned_ckpt = os.path.join(bert_checkpoints_folder, "model.ckpt-389")
    else:
        biobert_re_finetuned_vocab = os.path.join(os.path.join(os.getcwd(), "utils/biobert/re_outputs"), "vocab.txt")
        biobert_re_finetuned_config = os.path.join(os.path.join(os.getcwd(), "utils/biobert/re_outputs"), "bert_config.json")
        biobert_re_finetuned_ckpt = os.path.join(bert_checkpoints_folder, "model.ckpt-389")

    output_directory = os.path.join(os.getcwd(),"RE_try")
    import tempfile
    tempdir = tempfile.TemporaryDirectory(prefix="biobert_")
    output_directory = tempdir.name

    # re_dir = os.path.join(os.path.join(os.path.join(os.path.join(os.getcwd(),"datasets"),"RE"),"chemprot"),"scibert_preprocess")
    tokenization.validate_case_matches_checkpoint(False, biobert_re_finetuned_ckpt)

    ###### Extract BERT Configuration file --- LINE 969 of run_re.py 
    bert_config = modeling.BertConfig.from_json_file(biobert_re_finetuned_config)
    
    processor = BioBERTChemprotProcessor()

    ###### Note list of labels --- LINE 986 of run_re.py
    label_list = processor.get_labels()

    ###### Get Tokenizer --- LINE 988 of run_re.py
    tokenizer = tokenization.FullTokenizer(vocab_file=biobert_re_finetuned_vocab, do_lower_case=False)
    
    is_per_host = tf.contrib.tpu.InputPipelineConfig.PER_HOST_V2
    run_config = tf.contrib.tpu.RunConfig(cluster= None,
                                      master = None,
                                      model_dir=output_directory,
                                      save_checkpoints_steps=1000,
                                      tpu_config=tf.contrib.tpu.TPUConfig(
                                          iterations_per_loop=1000,
                                          num_shards=8,
                                          per_host_input_for_training=is_per_host))
    model_fn = model_fn_builder(bert_config=bert_config, 
                            num_labels=len(label_list), 
                            init_checkpoint=biobert_re_finetuned_ckpt,
                            learning_rate=5e-5,
                            num_train_steps=None,
                            num_warmup_steps=None,
                            use_tpu=False,
                            use_one_hot_embeddings=False)

    estimator = tf.contrib.tpu.TPUEstimator(use_tpu=False, model_fn=model_fn, config=run_config, predict_batch_size=8)
    predict_example = processor.get_test_example(sentences)
    #  predict_examples = processor.get_test_examples(re_dir)
    num_actual_predict_examples = len(predict_example)
    predict_file = os.path.join(output_directory, "predict.tf_record")
    file_based_convert_examples_to_features(predict_example, 
                                        label_list,
                                        128, 
                                        tokenizer,
                                        predict_file)
    predict_input_fn = file_based_input_fn_builder(input_file=predict_file,
                                               seq_length=128,
                                               is_training=False,
                                               drop_remainder=False)

    # prediction time testing
    # import time
    # times = [time.time()]
    # for i in range(5):
    #     result = estimator.predict(input_fn=predict_input_fn)
    #     for (i, prediction) in enumerate(result):
    #         probabilities = prediction["probabilities"]
    #         x = label_list[np.argmax(probabilities)]
    #     times.append(time.time())
    # for i in range(len(times)-1):
    #     print(times[i+1] - times[i])

    result = estimator.predict(input_fn=predict_input_fn)
    predictions = []
    for (i, prediction) in enumerate(result):
        probabilities = prediction["probabilities"]
        x = label_list[np.argmax(probabilities)]
        if x=="cpr:3":
            label_name = "UPREGULATOR|ACTIVATOR|INDIRECT_UPREGULATOR"
        elif x=="cpr:4":
            label_name = "DOWNREGULATOR|INHIBITOR|INDIRECT_DOWNREGULATOR"
        elif x=="cpr:5":
            label_name = "AGONIST|AGONIST‐ACTIVATOR|AGONIST‐INHIBITOR"
        elif x=="cpr:6":
            label_name = "ANTAGONIST"
        elif x=="cpr:9":
            label_name = "SUBSTRATE|PRODUCT_OF|SUBSTRATE_PRODUCT_OF"
        else:
            label_name = "No RELATION"

        predictions.append(label_name)

    tempdir.cleanup()
    return predictions


if __name__ == "__main__":
    data_try = 'Agonistic activity of << ICI 182 780 >> on activation of GSK 3β/[[ AKT ]] pathway in the rat uterus during the estrous cycle.'
    label_try = relationship_classification(data_try)
    print(label_try)
