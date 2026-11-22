#include "stm32f4xx_hal.h"
#include "adc.h"

void Error_Handler(void);

/*extern */ADC_HandleTypeDef hadc1;

// Заводское калибровочное значение VREFINT при 3.3В для STM32F411
// #define VREFINT_CAL_ADDR ((uint16_t*) ((uint32_t) 0x1FFF7A2A))
// #define VREFINT_CAL_VREF 3.30f

// Коэффициент обратного пересчета делителя: (R1 + R2) / R2
// Для R1 = 100 кОм, R2 = 200 кОм -> (100 + 200) / 200 = 1.5
#define R1     26300.0f
#define R2    100000.0f
#define DIVIDER_RATIO    ((R1+R2)/R2)//1.50f

//float divider_ratio = DIVIDER_RATIO;

void MX_ADC1_Init(void)
{
  hadc1.Instance = ADC1;
  // Предделитель частоты шины APB2 (если APB2 = 96/100 МГц, делим на 4 -> 24/25 МГц, что ниже лимита 36 МГц)
  hadc1.Init.ClockPrescaler         = ADC_CLOCK_SYNC_PCLK_DIV4;
  hadc1.Init.Resolution             = ADC_RESOLUTION_12B;             // 12 бит (0..4095)
  hadc1.Init.ScanConvMode           = DISABLE;                        // Одиночный режим (не скан)
  hadc1.Init.ContinuousConvMode     = DISABLE;                        // Измерение строго по команде старт
  hadc1.Init.DiscontinuousConvMode  = DISABLE;
  hadc1.Init.ExternalTrigConvEdge   = ADC_EXTERNALTRIGCONVEDGE_NONE;  // Запуск программно
  hadc1.Init.ExternalTrigConv       = ADC_SOFTWARE_START;
  hadc1.Init.DataAlign              = ADC_DATAALIGN_RIGHT;            // Выравнивание вправо
  hadc1.Init.NbrOfConversion        = 1;
  hadc1.Init.DMAContinuousRequests  = DISABLE;
  hadc1.Init.EOCSelection           = ADC_EOC_SINGLE_CONV;

  if(HAL_ADC_Init(&hadc1) != HAL_OK)
  {
    Error_Handler();
  }
  
  GPIO_InitTypeDef GPIO_InitStruct = {0};
  
  if(hadc1.Instance == ADC1)
  {
    // 1. Включаем тактирование самого модуля ADC1 и порта GPIOA
    __HAL_RCC_ADC1_CLK_ENABLE();
    __HAL_RCC_GPIOA_CLK_ENABLE();

    // 2. Настраиваем пин PA0 в аналоговый режим
    GPIO_InitStruct.Pin = GPIO_PIN_0;
    GPIO_InitStruct.Mode = GPIO_MODE_ANALOG; // Отключает цифровой буфер Шмитта
    GPIO_InitStruct.Pull = GPIO_NOPULL;      // Обязательно без подтяжек (иначе исказит делитель)
    HAL_GPIO_Init(GPIOA, &GPIO_InitStruct);
  }
}

// Вспомогательная функция чтения конкретного канала с усреднением
static uint32_t Read_ADC_Channel(uint32_t channel, uint8_t samples) {
    ADC_ChannelConfTypeDef sConfig = {0};
    sConfig.Channel = channel;
    sConfig.Rank = 1;
    sConfig.SamplingTime = ADC_SAMPLETIME_480CYCLES; // Максимальное время выборки!
    
    if (HAL_ADC_ConfigChannel(&hadc1, &sConfig) != HAL_OK) {
        Error_Handler();
    }

    uint32_t sum = 0;
    for (uint8_t i = 0; i < samples; i++) {
        HAL_ADC_Start(&hadc1);
        if (HAL_ADC_PollForConversion(&hadc1, 10) == HAL_OK) {
            sum += HAL_ADC_GetValue(&hadc1);
        }
        HAL_ADC_Stop(&hadc1);
    }
    return sum / samples;
}

// Основная функция получения напряжения батареи в Вольтах
float Get_Battery_Voltage(void)
{
  // 1. Читаем внутренний эталонный канал (усредняем по 16 замерам)
  uint32_t raw_vref = Read_ADC_Channel(ADC_CHANNEL_VREFINT, 16);

  // 2. Вычисляем реальное напряжение питания VDDA в данный момент
  float real_vdda = VREFINT_CAL_VREF * ((float)(*VREFINT_CAL_ADDR) / (float)raw_vref);
  real_vdda /= 1000.0f;

  // 3. Читаем канал с делителем батареи (например, ADC_CHANNEL_0 для пина PA0)
  uint32_t raw_bat = Read_ADC_Channel(ADC_CHANNEL_0, 16);

  // 4. Переводим попугаи АЦП в Вольты с учетом реального VDDA и делителя
  float pin_voltage = ((float)raw_bat / 4095.0f) * real_vdda;
  float battery_voltage = pin_voltage * DIVIDER_RATIO;

  return battery_voltage;
}
