import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
import seaborn as sns

# Параметры варианта 9
a = -4          # α (математическое ожидание)
sigma_sq = 16   # σ² (дисперсия)
sigma = 4       # σ (среднеквадратическое отклонение)
n = 12          # объем выборки
N = 250         # количество выборок
M = 666         # количество повторений для Части 2

print("=" * 60)
print(f"Параметры: α = {a}, σ² = {sigma_sq}, n = {n}, N = {N}, M = {M}")
print("Распределение Y: Логистическое с параметрами (0, 1)")
print("=" * 60)

# Часть 0: Исследование выборочного среднего
print("\n" + "="*50)
print("ЧАСТЬ 0: ИССЛЕДОВАНИЕ ВЫБОРОЧНОГО СРЕДНЕГО")
print("="*50)

# 1. Генерация N выборок объема n из нормального распределения

samples = np.random.normal(loc=a, scale=sigma, size=(N, n))

# 2. Вычисление выборочных средних
sample_means = np.mean(samples, axis=1)

# 3. Построение графиков
plt.figure(figsize=(15, 5))

# Кумулята относительных частот и теоретическая функция распределения
plt.subplot(1, 2, 1)
sorted_means = np.sort(sample_means)
empirical_cdf = np.arange(1, len(sorted_means) + 1) / len(sorted_means)
plt.step(sorted_means, empirical_cdf, where='post',
         label='Эмпирическая функция распределения', linewidth=2)

# Теоретическая функция распределения
x_theoretical = np.linspace(sorted_means.min(), sorted_means.max(), 1000)
theoretical_cdf = stats.norm.cdf(x_theoretical, loc=a, scale=sigma/np.sqrt(n))
plt.plot(x_theoretical, theoretical_cdf, 'r-',
         label='Теоретическая функция распределения', linewidth=2)

plt.xlabel('Выборочное среднее')
plt.ylabel('F(x)')
plt.title('Кумулята и теоретическая функция распределения\nвыборочного среднего')
plt.legend()
plt.grid(True, alpha=0.3)

# Гистограмма и теоретическая плотность
plt.subplot(1, 2, 2)
plt.hist(sample_means, bins=25, density=True, alpha=0.7,
         color='skyblue', edgecolor='black',
         label='Гистограмма относительных частот')

# Теоретическая плотность распределения
x_density = np.linspace(sample_means.min(), sample_means.max(), 1000)
theoretical_pdf = stats.norm.pdf(x_density, loc=a, scale=sigma/np.sqrt(n))
plt.plot(x_density, theoretical_pdf, 'r-', linewidth=2,
         label='Теоретическая плотность распределения')

plt.xlabel('Выборочное среднее')
plt.ylabel('Плотность вероятности')
plt.title('Гистограмма и теоретическая плотность\nраспределения выборочного среднего')
plt.legend()
plt.grid(True, alpha=0.3)

plt.tight_layout()
plt.show()

# 4. Вычисление характеристик распределения выборочных средних
mean_of_means = np.mean(sample_means)
median_of_means = np.median(sample_means)
variance_of_means = np.var(sample_means, ddof=1)
skewness = stats.skew(sample_means)
kurtosis = stats.kurtosis(sample_means)

print("\nХАРАКТЕРИСТИКИ РАСПРЕДЕЛЕНИЯ ВЫБОРОЧНЫХ СРЕДНИХ:")
print(f"Выборочное среднее: {mean_of_means:.4f} (теоретическое: {a:.4f})")
print(f"Медиана: {median_of_means:.4f}")
print(f"Выборочная дисперсия: {variance_of_means:.4f} (теоретическая: {sigma_sq/n:.4f})")
print(f"Коэффициент асимметрии: {skewness:.4f}")
print(f"Коэффициент эксцесса: {kurtosis:.4f}")

# 5. Подсчет количества выборочных средних, превышающих параметр a
count_above_a = np.sum(sample_means > a)
proportion_above_a = count_above_a / N
print(f"\nКоличество выборочных средних > α ({a}): {count_above_a} из {N}")
print(f"Относительная доля: {proportion_above_a:.4f} (теоретическая: 0.5000)")

# Часть I: Исследование выборочной дисперсии
print("\n" + "="*50)
print("ЧАСТЬ I: ИССЛЕДОВАНИЕ ВЫБОРОЧНОЙ ДИСПЕРСИИ")
print("="*50)

# Генерация новых выборок для исследования дисперсии
samples_var = np.random.normal(loc=a, scale=sigma, size=(N, n))

# Вычисление выборочной дисперсии
D_v = np.var(samples_var, axis=1, ddof=0)

# Статистики для D_v
mean_Dv = np.mean(D_v)
median_Dv = np.median(D_v)
var_Dv = np.var(D_v)

print(f"Выборочное среднее D_v: {mean_Dv:.4f}")
print(f"Медиана D_v: {median_Dv:.4f}")
print(f"Дисперсия D_v: {var_Dv:.4f}")

# Подсчет D_v < σ²
count_less_sigma = np.sum(D_v < sigma_sq)
prop_less_sigma = count_less_sigma / N
print(f"\nКоличество D_v < σ²: {count_less_sigma} из {N}")
print(f"Доля: {prop_less_sigma:.4f}")

# Вычисление Y = n * D_v / σ²
Y = n * D_v / sigma_sq

# Статистики для Y
mean_Y = np.mean(Y)
median_Y = np.median(Y)
var_Y = np.var(Y)
skew_Y = stats.skew(Y)
kurt_Y = stats.kurtosis(Y)

print(f"\nСТАТИСТИКИ ДЛЯ Y = n·D_v/σ²:")
print(f"Выборочное среднее Y: {mean_Y:.4f}")
print(f"Медиана Y: {median_Y:.4f}")
print(f"Дисперсия Y: {var_Y:.4f}")
print(f"Коэффициент асимметрии Y: {skew_Y:.4f}")
print(f"Коэффициент эксцесса Y: {kurt_Y:.4f}")

# Теоретические значения для Y (теорема Фишера)
df = n - 1
theoretical_mean = df
theoretical_median = stats.chi2.median(df)
theoretical_var = 2 * df
theoretical_skew = np.sqrt(8 / df)
theoretical_kurt = 12 / df

print(f"\nТЕОРЕТИЧЕСКИЕ ЗНАЧЕНИЯ ДЛЯ Y ~ χ²({df}):")
print(f"Математическое ожидание: {theoretical_mean:.4f}")
print(f"Медиана: {theoretical_median:.4f}")
print(f"Дисперсия: {theoretical_var:.4f}")
print(f"Коэффициент асимметрии: {theoretical_skew:.4f}")
print(f"Коэффициент эксцесса: {theoretical_kurt:.4f}")

# Визуализация для Части I
plt.figure(figsize=(15, 10))

# 1. Кумулята для D_v
plt.subplot(2, 3, 1)
x_sorted = np.sort(D_v)
y_ecdf = np.arange(1, N + 1) / N
plt.step(x_sorted, y_ecdf, where='post', linewidth=2)
plt.title('Кумулята относительных частот D_v')
plt.xlabel('D_v')
plt.ylabel('F(x)')
plt.grid(True, alpha=0.3)

# 2. Гистограмма для D_v
plt.subplot(2, 3, 2)
plt.hist(D_v, bins=25, density=True, alpha=0.7, color='lightblue', edgecolor='black')
plt.axvline(sigma_sq, color='red', linestyle='--', label=f'σ² = {sigma_sq}')
plt.title('Гистограмма относительных частот D_v')
plt.xlabel('D_v')
plt.ylabel('Плотность')
plt.legend()
plt.grid(True, alpha=0.3)

# 3. Гистограмма Y + теоретическая плотность
plt.subplot(2, 3, 3)
plt.hist(Y, bins=25, density=True, alpha=0.7, color='lightgreen',
         edgecolor='black', label='Выборочная плотность')

x_range = np.linspace(0, np.max(Y) * 1.1, 1000)
theoretical_pdf = stats.chi2.pdf(x_range, df)
plt.plot(x_range, theoretical_pdf, 'r-', linewidth=2,
         label=f'Теоретическая χ²({df})')

plt.title('Гистограмма Y и теоретическая плотность')
plt.xlabel('Y')
plt.ylabel('Плотность')
plt.legend()
plt.grid(True, alpha=0.3)

# 4. Кумулята Y + теоретическая функция распределения
plt.subplot(2, 3, 4)
y_sorted = np.sort(Y)
y_ecdf = np.arange(1, N + 1) / N
plt.step(y_sorted, y_ecdf, where='post', label='Эмпирическая F(y)', linewidth=2)

theoretical_cdf = stats.chi2.cdf(x_range, df)
plt.plot(x_range, theoretical_cdf, 'r-', linewidth=2,
         label=f'Теоретическая F(y)')

plt.title('Кумулята Y и теоретическая F(y)')
plt.xlabel('Y')
plt.ylabel('F(y)')
plt.legend()
plt.grid(True, alpha=0.3)

# 5. Q-Q plot
plt.subplot(2, 3, 5)
stats.probplot(Y, dist="chi2", sparams=(df,), plot=plt)
plt.title(f'Q-Q plot для Y vs χ²({df})')

# 6. Сравнение моментов
plt.subplot(2, 3, 6)
categories = ['Среднее', 'Дисперсия', 'Асимметрия', 'Эксцесс']
sample_values = [mean_Y, var_Y, skew_Y, kurt_Y]
theoretical_values = [theoretical_mean, theoretical_var, theoretical_skew, theoretical_kurt]

x_pos = np.arange(len(categories))
plt.bar(x_pos - 0.2, sample_values, 0.4, label='Выборочные', alpha=0.7)
plt.bar(x_pos + 0.2, theoretical_values, 0.4, label='Теоретические', alpha=0.7)

plt.xlabel('Моменты')
plt.ylabel('Значения')
plt.title('Сравнение выборочных и теоретических моментов')
plt.xticks(x_pos, categories)
plt.legend()
plt.grid(True, alpha=0.3)

plt.tight_layout()
plt.show()

# Часть II: Исследование средних значений выборочной дисперсии
print("\n" + "="*50)
print("ЧАСТЬ II: СРЕДНИЕ ЗНАЧЕНИЯ ВЫБОРОЧНОЙ ДИСПЕРСИИ")
print("="*50)

def compute_mean_variance(n, N, loc, scale):
    """Вычисление среднего значения выборочной дисперсии по N выборкам"""
    variances = []
    for _ in range(N):
        sample = np.random.normal(loc, scale, n)
        variance = np.var(sample, ddof=0)
        variances.append(variance)
    return np.mean(variances)

# Создание выборки из M средних значений выборочной дисперсии

mean_variances = []

print("Генерация данных...")
for i in range(M):
    mean_var = compute_mean_variance(n, N, a, sigma)
    mean_variances.append(mean_var)
    if (i + 1) % 100 == 0:
        print(f"Выполнено {i + 1}/{M} итераций")

mean_variances = np.array(mean_variances)

print(f"\nВыборка из {M} средних значений дисперсии создана")

# Статистики выборки средних дисперсий
mean_of_means = np.mean(mean_variances)
median_of_means = np.median(mean_variances)
std_of_means = np.std(mean_variances)

print(f"\nСТАТИСТИКИ ВЫБОРКИ СРЕДНИХ ДИСПЕРСИЙ:")
print(f"Среднее значение: {mean_of_means:.4f}")
print(f"Медиана: {median_of_means:.4f}")
print(f"Стандартное отклонение: {std_of_means:.4f}")
print(f"Теоретическое значение (σ²): {sigma_sq:.4f}")
print(f"Смещение: {mean_of_means - sigma_sq:.4f}")

# Визуализация для Части II
plt.figure(figsize=(15, 10))

# 1. Ящичковая диаграмма
plt.subplot(2, 2, 1)
sns.boxplot(y=mean_variances)
plt.axhline(y=sigma_sq, color='red', linestyle='--',
            label=f'Теоретическая σ² = {sigma_sq}')
plt.title('Ящичковая диаграмма средних значений\nвыборочной дисперсии')
plt.ylabel('Средняя дисперсия')
plt.legend()
plt.grid(True, alpha=0.3)

# 2. Гистограмма относительных частот
plt.subplot(2, 2, 2)
plt.hist(mean_variances, bins=25, density=True, alpha=0.7,
         color='lightblue', edgecolor='black')
plt.axvline(x=sigma_sq, color='red', linestyle='--',
            label=f'σ² = {sigma_sq}')
plt.title('Гистограмма средних значений\nвыборочной дисперсии')
plt.xlabel('Средняя дисперсия')
plt.ylabel('Плотность относительных частот')
plt.legend()
plt.grid(True, alpha=0.3)

# 3. Кумулята относительных частот
plt.subplot(2, 2, 3)
sorted_means = np.sort(mean_variances)
ecdf = np.arange(1, M + 1) / M
plt.step(sorted_means, ecdf, where='post', linewidth=2)
plt.title('Кумулята относительных частот\n(Эмпирическая функция распределения)')
plt.xlabel('Средняя дисперсия')
plt.ylabel('F(x)')
plt.grid(True, alpha=0.3)

# 4. Q-Q plot для проверки нормальности
plt.subplot(2, 2, 4)
stats.probplot(mean_variances, dist="norm", plot=plt)
plt.title('Q-Q plot для проверки нормальности')

plt.tight_layout()
plt.show()

# Дополнительный статистический анализ
Q1 = np.percentile(mean_variances, 25)
Q3 = np.percentile(mean_variances, 75)
IQR = Q3 - Q1
lower_bound = Q1 - 1.5 * IQR
upper_bound = Q3 + 1.5 * IQR
outliers = mean_variances[(mean_variances < lower_bound) | (mean_variances > upper_bound)]

confidence = 0.95
se = stats.sem(mean_variances)
h = se * stats.t.ppf((1 + confidence) / 2., M - 1)
ci_lower = mean_of_means - h
ci_upper = mean_of_means + h

print(f"\nДОПОЛНИТЕЛЬНЫЙ АНАЛИЗ:")
print(f"Минимальное значение: {np.min(mean_variances):.4f}")
print(f"Максимальное значение: {np.max(mean_variances):.4f}")
print(f"Размах: {np.ptp(mean_variances):.4f}")
print(f"Квартили: Q1={Q1:.4f}, Q2={median_of_means:.4f}, Q3={Q3:.4f}")
print(f"Межквартильный размах: {IQR:.4f}")
print(f"Количество выбросов: {len(outliers)}")
print(f"95% доверительный интервал для среднего: ({ci_lower:.4f}, {ci_upper:.4f})")

if ci_lower <= sigma_sq <= ci_upper:
    print("✓ Теоретическое значение σ² попадает в доверительный интервал")
else:
    print("✗ Теоретическое значение σ² НЕ попадает в доверительный интервал")

print("\n" + "="*60)
print("ВСЕ РАСЧЕТЫ ЗАВЕРШЕНЫ")
print("="*60)