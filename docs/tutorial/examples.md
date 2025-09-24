# Примеры использования Calibration Processing

## Пример 1: Базовая обработка

### Исходные данные

**Файлы CG-6:**

- `CG-6_0527_06072025.dat` - измерения прибора №527
- `CG-6_0528_06072025.dat` - измерения прибора №528

**Файл absolute.xlsx:**

| Station | gravity_eff | ste_eff | h_eff | a | b | ua | ub | covab |
|---------|-------------|---------|-------|---|---|----|----|-------|
| P01 | 979691473 | 0.00 | 0.68 | -335.17 | - 6.27 | 1.74 | 1.19 | -2.04 |
| P02 | 979777497 | 2.00 | 0.68 | -235.82 | - 5.44 | 2.17 | 1.50 | -3.21 |
| P03 | 979886785 | 1.00 | 0.68 | -266.79 | - 9.77 | 1.73 | 1.19 | -2.02 |
| P04 | 980023030 | 2.00 | 0.68 | -328.73 | -11.70 | 1.80 | 1.23 | -2.19 |
| P06 | 980069809 | 1.00 | 0.68 | -294.30 | - 3.24 | 2.08 | 1.44 | -2.93 |
| P05 | 980070551 | 2.00 | 0.68 | -275.11 | - 1.36 | 1.26 | 0.86 | -1.06 |
| P07 | 980185386 | 1.00 | 0.68 | -308.90 | - 4.35 | 3.16 | 2.18 | -6.75 |
| P08 | 980309127 | 1.00 | 0.68 | -316.47 | - 8.49 | 0.93 | 0.64 | -0.58 |

### Команда запуска

```bash
python scripts/calibration.py \
  --relative data/relative/*.dat \
  --absolute data/absolute.xlsx \
  --output results.xlsx \
  --method WLS \
  --drift_degree 2 \
  --calib_degree 1 \
  --meter_height 0.21
```

### Ожидаемые результаты

**calibration_parameters:**

| meter | calib_deg_1 | calib_deg_1_ste | diff_mean | diff_ste | diff_count |
|-------|-------------|-----------------|-----------|----------|------------|
| 23120527 | 1.000226 | 0.000009 | -0.004 | 0.010 | 7 |
| 23120528 | 0.999666 | 0.000008 | -0.002 | 0.011 | 7 |
| 23120531 | 0.999642 | 0.000009 | -0.005 | 0.011 | 7 |

## Пример 2: Обработка с высоким дрейфом

### Сценарий

Измерения с грубыми выбросами (на шумном пункте)

### Настройки

```bash
python scripts/calibration.py \
  --relative data/noisy/*.dat \
  --absolute data/absolute.xlsx \
  --output results_noisy.xlsx \
  --method RLM \
  --drift_degree 2 \
  --calib_degree 1 \
  --logging
```

**Особенности:**

- `method RLM` - робастный метод для устойчивости к выбросам
- `drift_degree 2` - квадратичная модель дрейфа
- `--logging` - подробное логирование процесса

## Пример 3: Прецизионные измерения

### Сценарий

Высокоточная калибровка с учетом квадратичных эффектов.

### Настройки

```bash
python scripts/calibration.py \
  --relative data/precision/*.dat \
  --absolute data/absolute.xlsx \
  --output results_precision.xlsx \
  --method WLS \
  --drift_degree 2 \
  --calib_degree 2 \
  --meter_height 0.205
```

**Особенности:**

- `calib_degree 2` - квадратичная калибровка
- Точная высота прибора `0.205` м

### Интерпретация квадратичной калибровки

**calibration_parameters:**

| meter | calib_deg_1 | calib_deg_2 | calib_deg_1_ste | calib_deg_2_ste |
|-------|-------------|-------------|-----------------|-----------------|
| 23120527 | 1.000182 | 8.77e-08 | 0.000029 | 5.93e-08 |

**Формула калибровки:**

> $\Delta g = 1.000182 \times \Delta g_\text{meas} - 8.77^{-6} \times \Delta g_\text{meas}^2$

<!-- ## Пример 4: Диагностика проблем

### Проблемный случай: высокие остатки

**Результат:**

| meter | diff_ste | diff_mean | diff_max |
|-------|----------|-----------|----------|
| 23120527 | 0.087 | 0.034 | 0.156 |

**Анализ:**

- `diff_ste = 0.087` мГал - превышает допустимое значение 0.01 мГал
- `diff_mean = 0.034` мГал - систематическая ошибка
- Требуется дополнительная диагностика

### Действия по устранению

1. **Проверка исходных данных:**

```bash
# Включить подробное логирование
python scripts/calibration.py --logging ... 
```

2. **Попробовать робастный метод:**

```bash
python scripts/calibration.py --method RLM ...
```

3. **Изменить модель дрейфа:**

```bash
python scripts/calibration.py --drift_degree 1 ...
``` -->

<!-- ## Пример 5: Пакетная обработка

### Скрипт для обработки множества проектов

```bash
#!/bin/bash
# process_all.sh

projects=("project1" "project2" "project3")

for project in "${projects[@]}"
do
    echo "Processing $project..."
    python scripts/calibration.py \
        --relative data/$project/relative/*.dat \
        --absolute data/$project/absolute.xlsx \
        --output results/$project_results.xlsx \
        --method WLS \
        --drift_degree 2 \
        --calib_degree 1 \
        --logging
    
    echo "$project completed"
done

echo "All projects processed"
```

### Автоматический анализ качества

```python
# quality_check.py
import pandas as pd
import os

results_folder = "results"
quality_report = []

for file in os.listdir(results_folder):
    if file.endswith("_results.xlsx"):
        df = pd.read_excel(f"{results_folder}/{file}", sheet_name='calibration_parameters')
        
        project = file.replace("_results.xlsx", "")
        quality = "PASS" if df['diff_ste'].max() < 0.01 else "FAIL"
        
        quality_report.append({
            'project': project,
            'max_std': df['diff_ste'].max(),
            'mean_coeff': df['calib_deg_1'].mean(),
            'quality': quality
        })

report_df = pd.DataFrame(quality_report)
report_df.to_excel("quality_summary.xlsx", index=False)
print("Quality report saved to quality_summary.xlsx")
``` -->

<!-- ## Пример 6: Сравнение методов

### Тестирование разных подходов на одних данных

```bash
# Взвешенный МНК
python scripts/calibration.py --method WLS ... --output results_wls.xlsx

# Обычный МНК  
python scripts/calibration.py --method OLS ... --output results_ols.xlsx

# Робастный МНК
python scripts/calibration.py --method RLM ... --output results_rlm.xlsx
```

### Сравнительная таблица

| Метод | Коэффициент | Ошибка коэфф. | Остатки (СКО) | Время |
|-------|-------------|---------------|---------------|-------|
| WLS | 1.0019 | 0.0003 | 0.008 | 0.5с |
| OLS | 1.0021 | 0.0005 | 0.011 | 0.3с |
| RLM | 1.0017 | 0.0004 | 0.007 | 1.2с |

**Рекомендация:** WLS обеспечивает оптимальный баланс точности и скорости.

## Пример 7: Работа с различными высотами

### Сценарий: измерения на разных высотах установки прибора

```bash
# Стандартная высота 0.21 м
python scripts/calibration.py --meter_height 0.21 ... --output results_h21.xlsx

# Увеличенная высота 0.30 м  
python scripts/calibration.py --meter_height 0.30 ... --output results_h30.xlsx

# Минимальная высота 0.15 м
python scripts/calibration.py --meter_height 0.15 ... --output results_h15.xlsx
```

### Влияние высоты на результат

При градиенте **a = -0.308 мГал/м**:

| Высота | Поправка к g | Коэффициент калибровки |
|--------|--------------|------------------------|
| 0.15 м | +0.018 мГал | 1.0019 |
| 0.21 м | 0.000 мГал | 1.0019 |
| 0.30 м | -0.028 мГал | 1.0019 |

**Вывод:** Высота прибора влияет на абсолютные значения, но не на калибровочные коэффициенты. -->

---

*Все примеры основаны на реальных сценариях использования. Адаптируйте параметры под специфику ваших данных и требований.*