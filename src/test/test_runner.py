import os
from nose import SkipTest
from nose.tools import assert_true, assert_equal
from loom.test.util import for_each_dataset
from distributions.fileutil import tempdir, json_load
import loom.format
import loom.runner
from subprocess import CalledProcessError

CLEANUP_ON_ERROR = int(os.environ.get('CLEANUP_ON_ERROR', 1))


@for_each_dataset
def test_loom(meta, data, mask, latent, predictor, **unused):
    kind_count = len(json_load(predictor)['structure'])
    if kind_count > 1:
        raise SkipTest('TODO allow multiple kinds')

    with tempdir(cleanup_on_error=CLEANUP_ON_ERROR):
        model = os.path.abspath('model.pb')
        loom.format.import_latent(meta, latent, model)
        assert_true(os.path.exists(model))

        values = os.path.abspath('rows.pbs')
        loom.format.import_data(meta, data, mask, values)
        assert_true(os.path.exists(values))

        groups = os.path.abspath('groups')
        os.mkdir(groups)
        loom.runner.run(model, values, groups)
        assert_equal(len(os.listdir(groups)), kind_count)
        assert_true(os.path.exists(groups))
