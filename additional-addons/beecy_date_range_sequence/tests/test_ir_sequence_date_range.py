import pytest
from .fixtures import *
from odoo.exceptions import ValidationError


@pytest.mark.parametrize('test_input,expected', [
    ({
        'df': datetime.strptime('2022-01-01', '%Y-%m-%d'),
        'dt': datetime.strptime('2022-12-31', '%Y-%m-%d'),
        'get_df': datetime.strptime('2022-01-01', '%Y-%m-%d'),
        'get_dt': datetime.strptime('2022-12-31', '%Y-%m-%d'),
    }, False),
    ({
        'df': datetime.strptime('2022-02-01', '%Y-%m-%d'),
        'dt': datetime.strptime('2022-12-31', '%Y-%m-%d'),
        'get_df': datetime.strptime('2022-01-01', '%Y-%m-%d'),
        'get_dt': datetime.strptime('2022-12-31', '%Y-%m-%d'),
    }, True),
    ({
        'df': datetime.strptime('2022-01-01', '%Y-%m-%d'),
        'dt': datetime.strptime('2022-11-30', '%Y-%m-%d'),
        'get_df': datetime.strptime('2022-01-01', '%Y-%m-%d'),
        'get_dt': datetime.strptime('2022-12-31', '%Y-%m-%d'),
    }, True),
    ({
        'df': datetime.strptime('2022-02-01', '%Y-%m-%d'),
        'dt': datetime.strptime('2022-11-30', '%Y-%m-%d'),
        'get_df': datetime.strptime('2022-01-01', '%Y-%m-%d'),
        'get_dt': datetime.strptime('2022-12-31', '%Y-%m-%d'),
    }, True)
])
def test__check_date_from_and_to(
        model_seq_range, seq_range,
        mocker, test_input, expected
):
    date_from = test_input['df'].date()
    date_to = test_input['dt'].date()
    get_date_from = test_input['get_df'].date()
    get_date_to = test_input['get_dt'].date()
    seq_range.range = 'year'
    # spy get date from range
    spy_get_date_from_range = mocker.patch.object(
        type(seq_range),
        '_get_date_from_range',
        return_value=(
            get_date_from,
            get_date_to,
        ),
    )
    # spy check duplicate
    spy_check_duplicate = mocker.patch.object(
        type(model_seq_range),
        'check_date_range_duplicate',
        return_value=True,
    )
    if expected:
        with pytest.raises(ValidationError) as excinfo:
            model_seq_range.create({
                'sequence_id': seq_range.id,
                'date_from': date_from,
                'date_to': date_to,
            })
        str_err = 'Please set date from equal %s and date to %s' \
                  % (str(get_date_from), str(get_date_to))
        assert str(excinfo.value) == str_err
    else:
        date_range = model_seq_range.create({
            'sequence_id': seq_range.id,
            'date_from': date_from,
            'date_to': date_to,
        })
        spy_get_date_from_range.assert_called_once_with(
            seq_range.range, date_range.date_from
        )
        spy_check_duplicate.assert_called_once_with(
            date_from,
            date_to,
        )
        assert True


@pytest.mark.parametrize('test_input,expected', [
    ({
        'df': datetime.strptime('2022-02-01', '%Y-%m-%d'),
        'dt': datetime.strptime('2022-02-28', '%Y-%m-%d'),
    }, False),
    ({
        'df': datetime.strptime('2022-03-01', '%Y-%m-%d'),
        'dt': datetime.strptime('2022-03-31', '%Y-%m-%d'),
    }, True),
])
def test_check_date_range_duplicate(
        model_seq_range, seq_range,
        test_input, expected
):
    seq_range.range = 'month'
    date_from = datetime.strptime('2022-03-01', '%Y-%m-%d')
    date_to = datetime.strptime('2022-03-31', '%Y-%m-%d')
    date_range = model_seq_range.create({
        'sequence_id': seq_range.id,
        'date_from': date_from.date(),
        'date_to': date_to.date(),
    })
    if expected:
        with pytest.raises(ValidationError) as excinfo:
            date_range_2 = model_seq_range.create({
                'sequence_id': seq_range.id,
                'date_from': date_from.date(),
                'date_to': date_to.date(),
            })
            date_range_2.check_date_range_duplicate(
                test_input['df'].date(),
                test_input['dt'].date(),
            )
        assert str(excinfo.value) == 'Please Check Date Range Duplicate'
    else:
        date_range.check_date_range_duplicate(
            test_input['df'].date(),
            test_input['dt'].date(),
        )
        assert True
