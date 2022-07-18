import pytest
from pytest_tr_odoo.fixtures import env
from datetime import datetime


@pytest.fixture
def model_seq(env):
    return env['ir.sequence']


@pytest.fixture
def model_seq_range(env):
    return env['ir.sequence.date_range']


@pytest.fixture
def seq_not_range(model_seq):
    return model_seq.create({
        'name': 'Sequence',
        'use_date_range': False,
    })


@pytest.fixture
def seq_range(model_seq):
    return model_seq.create({
        'name': 'Sequence',
        'use_date_range': True,
    })


@pytest.fixture
def fix_date():
    fix_date = datetime.strptime('2022-02-23', '%Y-%m-%d')
    return fix_date
