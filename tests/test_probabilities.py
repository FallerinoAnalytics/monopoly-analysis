import monopoly_analysis.probabilities as moprob
import pytest


def test_doubles_probs():
    """Test: Returns correct probabilities for doubles."""
    obj = moprob.Probabilities()
    # ACT
    result = obj.get_doubles_probabilities()

    # ASSERT
    expected = {
        2: 0.0278,
        4: 0.0278,
        6: 0.0278,
        8: 0.0278,
        10: 0.0278,
        12: 0.0278
    }
    assert result == expected
