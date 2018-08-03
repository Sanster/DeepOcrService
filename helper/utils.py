import os
import tensorflow as tf


def load_graph(frozen_graph_filename):
    # We load the protobuf file from the disk and parse it to retrieve the
    # unserialized graph_def
    with tf.gfile.GFile(frozen_graph_filename, "rb") as f:
        graph_def = tf.GraphDef()
        graph_def.ParseFromString(f.read())

    # Then, we import the graph_def into a new Graph and returns it
    with tf.Graph().as_default() as graph:
        # The name var will prefix every op/nodes in your graph
        # Since we load everything in a new graph, this is not needed
        tf.import_graph_def(graph_def)
    return graph


# http://cv-tricks.com/tensorflow-tutorial/save-restore-tensorflow-models-quick-complete-tutorial/
def restore_ckpt(sess, checkpoint_dir):
    print("Restoring checkpoint from: " + checkpoint_dir)

    ckpt = tf.train.latest_checkpoint(checkpoint_dir)
    if ckpt is None:
        print("Checkpoint not found")
        exit(-1)

    meta_file = ckpt + '.meta'
    try:
        print('Restore graph from {}'.format(meta_file))
        print('Restore variables from {}'.format(ckpt))
        saver = tf.train.import_meta_graph(meta_file)
        saver.restore(sess, ckpt)
    except Exception:
        raise Exception("Can not restore from {}".format(checkpoint_dir))


def load_ckpt(ckpt):
    """
    :param ckpt: ckpt 目录或者 pb 文件
    """

    config = tf.ConfigProto(allow_soft_placement=True)
    config.gpu_options.per_process_gpu_memory_fraction = 0.2

    if os.path.isdir(ckpt):
        graph = tf.Graph()
        with graph.as_default():
            sess = tf.Session(config=config)
            restore_ckpt(sess, os.path.abspath(ckpt))

    elif os.path.isfile(ckpt) and ckpt.endswith('.pb'):
        graph = load_graph(ckpt)
        with graph.as_default():
            sess = tf.Session(graph=graph, config=config)
    else:
        print("Load ckpt failed")
        exit(-1)

    return sess, graph
