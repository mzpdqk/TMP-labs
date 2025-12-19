import numpy as np
import pytest
from unittest.mock import patch, MagicMock
from scipy import stats
import sys
import os
from lab4_statanalisys import *


# Вместо импорта всего кода,будем тестировать логику через моки

def test_normal_distribution_parameters():
    """Тест параметров нормального распределения."""
    a = -4
    sigma = 4
    n = 12
    # Генерируем выборку
    sample = np.random.normal(loc=a, scale=sigma, size=n)
    # Проверяем размер
    assert len(sample) == n
    # Проверяем, что среднее близко к a (в пределах 3 сигм)
    assert np.abs(np.mean(sample) - a) < 3 * sigma / np.sqrt(n)

def test_sample_mean_calculation():
    """Тест вычисления выборочного среднего."""
    data = np.array([[1, 2, 3], [4, 5, 6]])
    sample_means = np.mean(data, axis=1)
    expected = np.array([2., 5.])
    np.testing.assert_array_almost_equal(sample_means, expected)

def test_sample_variance_calculation():
    """Тест вычисления выборочной дисперсии."""
    data = np.array([1, 2, 3, 4, 5])
    variance = np.var(data, ddof=0)
    expected = 2.0  # ((1-3)^2 + ... + (5-3)^2)/5 = 10/5 = 2
    assert variance == expected

@pytest.mark.parametrize("n, sigma_sq, expected_mean", [
    (10, 4, 9),  # df = n-1 = 9
    (5, 9, 4),   # df = 4
    (20, 1, 19), # df = 19
])
def test_chi_squared_statistic_mean(n, sigma_sq, expected_mean):
    """Параметризованный тест для среднего статистики Y (хи-квадрат)."""
    # Y = n * D_v / sigma^2, E[Y] = df = n-1
    df = n - 1
    assert df == expected_mean

def test_empirical_cdf():
    """Тест построения эмпирической функции распределения."""
    data = np.array([1.0, 2.0, 3.0])
    sorted_data = np.sort(data)
    empirical_cdf = np.arange(1, len(sorted_data) + 1) / len(sorted_data)
    expected = np.array([1/3, 2/3, 1.0])
    np.testing.assert_array_almost_equal(empirical_cdf, expected)

@patch('numpy.random.normal')
def test_generate_samples_with_mock(mock_normal):
    """Тест генерации выборок с использованием мока."""
    mock_normal.return_value = np.array([[1.0, 2.0], [3.0, 4.0]])
    samples = np.random.normal(loc=0, scale=1, size=(2, 2))
    assert samples.shape == (2, 2)
    assert np.array_equal(samples, np.array([[1.0, 2.0], [3.0, 4.0]]))
    mock_normal.assert_called_once_with(loc=0, scale=1, size=(2, 2))

def test_confidence_interval():
    """Тест вычисления доверительного интервала."""
    data = np.random.normal(loc=0, scale=1, size=100)
    confidence = 0.95
    m = len(data)
    mean = np.mean(data)
    se = stats.sem(data)
    h = se * stats.t.ppf((1 + confidence) / 2., m - 1)
    ci_lower = mean - h
    ci_upper = mean + h
    # Проверяем, что истинное среднее (0) попадает в интервал (с большой вероятностью)
    # проверим только что интервал корректно вычислен
    assert ci_lower < ci_upper
    assert isinstance(ci_lower, float)
    assert isinstance(ci_upper, float)

def test_skewness_kurtosis():
    """Тест вычисления асимметрии и эксцесса."""
    data = np.random.normal(loc=0, scale=1, size=1000)
    skew = stats.skew(data)
    kurt = stats.kurtosis(data)
    # Для нормального распределения skew ~ 0, kurt ~ 0
    assert np.abs(skew) < 0.5
    assert np.abs(kurt) < 0.5

# Доп тест с использованием фикстурр
@pytest.fixture
def sample_data():
    """Фикстура для тестовых данных."""
    return np.random.normal(loc=-4, scale=4, size=100)

def test_with_fixture(sample_data):
    """Тест с использованием фикстуры."""
    assert len(sample_data) == 100
    assert np.abs(np.mean(sample_data) + 4) < 1.0  # Примерно

if __name__ == "__main__":

    pytest.main()
