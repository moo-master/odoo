import pytest
from .fixtures import *


def test__onchange_use_date_range(
        seq_range, seq_not_range
):
    seq_not_range._onchange_use_date_range()
    seq_range._onchange_use_date_range()
    assert seq_range.range == 'year'
    assert seq_not_range.range is False


def test__get_date_to_and_date_from_week(
        seq_range, fix_date
):
    df = datetime.strptime('2022-02-21', '%Y-%m-%d')
    dt = datetime.strptime('2022-02-27', '%Y-%m-%d')
    date_from, date_to = seq_range._get_date_to_and_date_from_week(
        fix_date
    )
    assert date_from == df
    assert date_to == dt


@pytest.mark.parametrize('test_input,expected', [
    (datetime.strptime('2022-02-23', '%Y-%m-%d'), {
        'df': datetime.strptime('2022-02-01', '%Y-%m-%d'),
        'dt': datetime.strptime('2022-02-28', '%Y-%m-%d'),
    }),
    (datetime.strptime('2022-12-23', '%Y-%m-%d'), {
        'df': datetime.strptime('2022-12-01', '%Y-%m-%d'),
        'dt': datetime.strptime('2022-12-31', '%Y-%m-%d'),
    })
])
def test__get_date_to_and_date_from_month(
        seq_range, test_input, expected
):
    date_from, date_to = seq_range._get_date_to_and_date_from_month(
        test_input
    )
    assert date_from == expected['df']
    assert date_to == expected['dt']


def test__get_date_to_and_date_from_year(
        seq_range, fix_date
):
    df = datetime.strptime('2022-01-01', '%Y-%m-%d')
    dt = datetime.strptime('2022-12-31', '%Y-%m-%d')
    date_from, date_to = seq_range._get_date_to_and_date_from_year(
        fix_date
    )
    assert date_from == df
    assert date_to == dt


@pytest.mark.parametrize('test_input,expected', [
    ('year', 'year'),
    ('month', 'month'),
    ('week', 'week'),
])
def test__get_date_from_range(
        test_input, expected, fix_date, mocker, seq_range
):
    # mock get year
    spy_year = mocker.patch.object(
        type(seq_range),
        '_get_date_to_and_date_from_year',
        return_value=(
            datetime.strptime('2022-01-01', '%Y-%m-%d'),
            datetime.strptime('2022-12-31', '%Y-%m-%d'),
        ),
    )
    # mock get month
    spy_month = mocker.patch.object(
        type(seq_range),
        '_get_date_to_and_date_from_month',
        return_value=(
            datetime.strptime('2022-01-01', '%Y-%m-%d'),
            datetime.strptime('2022-12-31', '%Y-%m-%d'),
        ),
    )
    # mock get week
    spy_week = mocker.patch.object(
        type(seq_range),
        '_get_date_to_and_date_from_week',
        return_value=(
            datetime.strptime('2022-01-01', '%Y-%m-%d'),
            datetime.strptime('2022-12-31', '%Y-%m-%d'),
        ),
    )
    seq_range._get_date_from_range(
        test_input, fix_date
    )
    if expected == 'year':
        spy_year.assert_called_once_with(
            fix_date
        )
    elif expected == 'month':
        spy_month.assert_called_once_with(
            fix_date
        )
    else:
        spy_week.assert_called_once_with(
            fix_date
        )


def test__create_date_range_seq(
        seq_range, fix_date, mocker, model_seq_range
):
    date_from = datetime.strptime('2022-01-01', '%Y-%m-%d')
    date_to = datetime.strptime('2022-12-31', '%Y-%m-%d')
    # mock call function get date from range
    spy_get_date_from_range = mocker.patch.object(
        type(seq_range),
        '_get_date_from_range',
        return_value=(
            datetime.strptime('2022-01-01', '%Y-%m-%d'),
            datetime.strptime('2022-12-31', '%Y-%m-%d'),
        ),
    )
    # mock create date range
    spy_date_range = mocker.patch.object(
        type(model_seq_range),
        'create',
        return_value=True,
    )
    seq_range.range = 'year'
    seq_date_range = seq_range._create_date_range_seq(
        fix_date
    )
    spy_get_date_from_range.assert_called_once_with(
        seq_range.range, fix_date.date()
    )
    spy_date_range.assert_called_once_with({
        'date_from': date_from,
        'date_to': date_to,
        'sequence_id': seq_range.id,
    })
    assert seq_date_range == 1
