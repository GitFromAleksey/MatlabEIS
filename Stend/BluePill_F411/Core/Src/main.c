/* USER CODE BEGIN Header */
/**
  ******************************************************************************
  * @file           : main.c
  * @brief          : Main program body
  ******************************************************************************
  * @attention
  *
  * Copyright (c) 2025 STMicroelectronics.
  * All rights reserved.
  *
  * This software is licensed under terms that can be found in the LICENSE file
  * in the root directory of this software component.
  * If no LICENSE file comes with this software, it is provided AS-IS.
  *
  ******************************************************************************
  */
/* USER CODE END Header */
/* Includes ------------------------------------------------------------------*/
#include "main.h"
#include "usb_device.h"

/* Private includes ----------------------------------------------------------*/
/* USER CODE BEGIN Includes */
#include <stdbool.h>
#include "usbd_cdc_if.h"
/* USER CODE END Includes */

/* Private typedef -----------------------------------------------------------*/
/* USER CODE BEGIN PTD */

/* USER CODE END PTD */

/* Private define ------------------------------------------------------------*/
/* USER CODE BEGIN PD */

/* USER CODE END PD */

/* Private macro -------------------------------------------------------------*/
/* USER CODE BEGIN PM */

/* USER CODE END PM */

/* Private variables ---------------------------------------------------------*/
ADC_HandleTypeDef hadc1;
DMA_HandleTypeDef hdma_adc1;

/* USER CODE BEGIN PV */
#define ADC_BIG_DATA_BUF_SIZE    30000u // 30468u
extern USBD_HandleTypeDef hUsbDeviceFS;
typedef enum
{
  MODE_PGM_START,
  MODE_ADC_COLLECTING,
  MODE_ADC_COLLECT_STOP,
  MODE_USB_TX,
  MODE_STOP
} work_modes_t;

// номера АЦП каналов в массиве AdcDmaDataBuf
enum
{
  ADC_IN_0 = 0,
  ADC_IN_1 = 1,
  ADC_DATA_BUF_SIZE
};

typedef struct
{
  uint16_t data[ADC_DATA_BUF_SIZE];
} adc_channels_array_t;

// структура массива данных
typedef struct
{
  adc_channels_array_t channels[ADC_BIG_DATA_BUF_SIZE];
  uint32_t channel_index;
} adc_big_array_t;

work_modes_t WorkMode;
uint32_t DataCollectTime;
volatile uint16_t DmaData[ADC_DATA_BUF_SIZE];
volatile adc_big_array_t AdcBigDataBuf;

bool DataCollecionIsStarted = false;
/* USER CODE END PV */

/* Private function prototypes -----------------------------------------------*/
void SystemClock_Config(void);
static void MX_GPIO_Init(void);
static void MX_DMA_Init(void);
static void MX_ADC1_Init(void);
/* USER CODE BEGIN PFP */
// ----------------------------------------------------------------------------
// старт преобразования каналов АЦП
void AdcStartConversion(void)
{
  uint32_t index = AdcBigDataBuf.channel_index;

//  HAL_ADC_Start_DMA(&hadc1, (uint32_t*)AdcBigDataBuf.channels[index].data, ADC_DATA_BUF_SIZE);
  HAL_ADC_Start_DMA(&hadc1, (uint32_t*)DmaData, ADC_DATA_BUF_SIZE);

//  AdcBigDataBuf.channel_index++;
//  if(AdcBigDataBuf.channel_index == ADC_BIG_DATA_BUF_SIZE)
//  {
//    DataCollectTime = HAL_GetTick() - DataCollectTime;
//    DataCollecionIsStarted = false;
//  }
}
// ----------------------------------------------------------------------------
// запуск заполнения массива данными
void StartDataCollection(void)
{
  if(DataCollecionIsStarted == true)
    return;

  DataCollecionIsStarted = true;
  AdcBigDataBuf.channel_index = 0;

  DataCollectTime = HAL_GetTick();
  AdcStartConversion();
}
// ----------------------------------------------------------------------------
void HAL_ADC_ConvHalfCpltCallback(ADC_HandleTypeDef* hadc)
{
//  AdcStartConversion();
  HAL_GPIO_TogglePin(GPIOA, GPIO_PIN_9);
}
void HAL_ADC_ConvCpltCallback(ADC_HandleTypeDef *hadc)
{
//  HAL_ADC_Stop_DMA(&hadc1);
  if(DataCollecionIsStarted)
    AdcStartConversion();

  AdcBigDataBuf.channels[AdcBigDataBuf.channel_index].data[0] = DmaData[0];
  AdcBigDataBuf.channels[AdcBigDataBuf.channel_index].data[1] = DmaData[1];

  AdcBigDataBuf.channel_index++;
  if(AdcBigDataBuf.channel_index == ADC_BIG_DATA_BUF_SIZE)
  {
    DataCollectTime = HAL_GetTick() - DataCollectTime;
    DataCollecionIsStarted = false;
  }
}
// ----------------------------------------------------------------------------
/* USER CODE END PFP */

/* Private user code ---------------------------------------------------------*/
/* USER CODE BEGIN 0 */
#define USB_TX_BUF_SIZE    100u
/* USER CODE END 0 */

/**
  * @brief  The application entry point.
  * @retval int
  */
int main(void)
{

  /* USER CODE BEGIN 1 */
  char usb_tx_buf[USB_TX_BUF_SIZE];
  uint32_t usb_tx_data_index;
  /* USER CODE END 1 */

  /* MCU Configuration--------------------------------------------------------*/

  /* Reset of all peripherals, Initializes the Flash interface and the Systick. */
  HAL_Init();

  /* USER CODE BEGIN Init */

  /* USER CODE END Init */

  /* Configure the system clock */
  SystemClock_Config();

  /* USER CODE BEGIN SysInit */

  /* USER CODE END SysInit */

  /* Initialize all configured peripherals */
  MX_GPIO_Init();
  MX_DMA_Init();
  MX_ADC1_Init();
  MX_USB_DEVICE_Init();
  /* USER CODE BEGIN 2 */
  WorkMode = MODE_PGM_START;
  /* USER CODE END 2 */

  /* Infinite loop */
  /* USER CODE BEGIN WHILE */
  while (1)
  {
//    StartDataCollection();
//    HAL_GPIO_TogglePin(LED_BLUE_GPIO_Port, LED_BLUE_Pin);
//    HAL_Delay(2000);

    switch(WorkMode)
    {
      case MODE_PGM_START:
        StartDataCollection();
        WorkMode = MODE_ADC_COLLECTING;
        break;
      case MODE_ADC_COLLECTING:
        if(!DataCollecionIsStarted)
          WorkMode = MODE_ADC_COLLECT_STOP;
        break;
      case MODE_ADC_COLLECT_STOP:
        usb_tx_data_index = 0;
        WorkMode = MODE_USB_TX;
        break;
      case MODE_USB_TX:
        sprintf(usb_tx_buf, "{\"TIME_STAMP\":%d,\"Ch0\":%d,\"Ch1\":%d}\r\n",
                usb_tx_data_index,
                AdcBigDataBuf.channels[usb_tx_data_index].data[ADC_IN_0],
                AdcBigDataBuf.channels[usb_tx_data_index].data[ADC_IN_1]);
        if( CDC_Transmit_FS((uint8_t*)usb_tx_buf, strlen(usb_tx_buf)) == USBD_OK)
        {
          usb_tx_data_index++;
          if(usb_tx_data_index >= ADC_BIG_DATA_BUF_SIZE)
          {
            usb_tx_data_index = 0;
            WorkMode = MODE_STOP;
            USBD_CDC_HandleTypeDef *hcdc = (USBD_CDC_HandleTypeDef*)hUsbDeviceFS.pClassData;
            while(hcdc->TxState != 0) {}
            sprintf(usb_tx_buf, "---------------------------------------\r\n");
            CDC_Transmit_FS((uint8_t*)usb_tx_buf, strlen(usb_tx_buf));
          }
        }
        break;
      case MODE_STOP:

        break;
      default:
        WorkMode = MODE_PGM_START;
        break;
    }

    /* USER CODE END WHILE */

    /* USER CODE BEGIN 3 */
  }
  /* USER CODE END 3 */
}

/**
  * @brief System Clock Configuration
  * @retval None
  */
void SystemClock_Config(void)
{
  RCC_OscInitTypeDef RCC_OscInitStruct = {0};
  RCC_ClkInitTypeDef RCC_ClkInitStruct = {0};

  /** Configure the main internal regulator output voltage
  */
  __HAL_RCC_PWR_CLK_ENABLE();
  __HAL_PWR_VOLTAGESCALING_CONFIG(PWR_REGULATOR_VOLTAGE_SCALE1);

  /** Initializes the RCC Oscillators according to the specified parameters
  * in the RCC_OscInitTypeDef structure.
  */
  RCC_OscInitStruct.OscillatorType = RCC_OSCILLATORTYPE_HSE;
  RCC_OscInitStruct.HSEState = RCC_HSE_ON;
  RCC_OscInitStruct.PLL.PLLState = RCC_PLL_ON;
  RCC_OscInitStruct.PLL.PLLSource = RCC_PLLSOURCE_HSE;
  RCC_OscInitStruct.PLL.PLLM = 15;
  RCC_OscInitStruct.PLL.PLLN = 144;
  RCC_OscInitStruct.PLL.PLLP = RCC_PLLP_DIV4;
  RCC_OscInitStruct.PLL.PLLQ = 5;
  if (HAL_RCC_OscConfig(&RCC_OscInitStruct) != HAL_OK)
  {
    Error_Handler();
  }

  /** Initializes the CPU, AHB and APB buses clocks
  */
  RCC_ClkInitStruct.ClockType = RCC_CLOCKTYPE_HCLK|RCC_CLOCKTYPE_SYSCLK
                              |RCC_CLOCKTYPE_PCLK1|RCC_CLOCKTYPE_PCLK2;
  RCC_ClkInitStruct.SYSCLKSource = RCC_SYSCLKSOURCE_PLLCLK;
  RCC_ClkInitStruct.AHBCLKDivider = RCC_SYSCLK_DIV1;
  RCC_ClkInitStruct.APB1CLKDivider = RCC_HCLK_DIV2;
  RCC_ClkInitStruct.APB2CLKDivider = RCC_HCLK_DIV1;

  if (HAL_RCC_ClockConfig(&RCC_ClkInitStruct, FLASH_LATENCY_1) != HAL_OK)
  {
    Error_Handler();
  }
}

/**
  * @brief ADC1 Initialization Function
  * @param None
  * @retval None
  */
static void MX_ADC1_Init(void)
{

  /* USER CODE BEGIN ADC1_Init 0 */

  /* USER CODE END ADC1_Init 0 */

  ADC_ChannelConfTypeDef sConfig = {0};

  /* USER CODE BEGIN ADC1_Init 1 */

  /* USER CODE END ADC1_Init 1 */

  /** Configure the global features of the ADC (Clock, Resolution, Data Alignment and number of conversion)
  */
  hadc1.Instance = ADC1;
  hadc1.Init.ClockPrescaler = ADC_CLOCK_SYNC_PCLK_DIV2;
  hadc1.Init.Resolution = ADC_RESOLUTION_12B;
  hadc1.Init.ScanConvMode = ENABLE;
  hadc1.Init.ContinuousConvMode = DISABLE;
  hadc1.Init.DiscontinuousConvMode = DISABLE;
  hadc1.Init.ExternalTrigConvEdge = ADC_EXTERNALTRIGCONVEDGE_NONE;
  hadc1.Init.ExternalTrigConv = ADC_SOFTWARE_START;
  hadc1.Init.DataAlign = ADC_DATAALIGN_RIGHT;
  hadc1.Init.NbrOfConversion = 2;
  hadc1.Init.DMAContinuousRequests = DISABLE;
  hadc1.Init.EOCSelection = ADC_EOC_SEQ_CONV;
  if (HAL_ADC_Init(&hadc1) != HAL_OK)
  {
    Error_Handler();
  }

  /** Configure for the selected ADC regular channel its corresponding rank in the sequencer and its sample time.
  */
  sConfig.Channel = ADC_CHANNEL_0;
  sConfig.Rank = 1;
  sConfig.SamplingTime = ADC_SAMPLETIME_15CYCLES;
  if (HAL_ADC_ConfigChannel(&hadc1, &sConfig) != HAL_OK)
  {
    Error_Handler();
  }

  /** Configure for the selected ADC regular channel its corresponding rank in the sequencer and its sample time.
  */
  sConfig.Channel = ADC_CHANNEL_1;
  sConfig.Rank = 2;
  if (HAL_ADC_ConfigChannel(&hadc1, &sConfig) != HAL_OK)
  {
    Error_Handler();
  }
  /* USER CODE BEGIN ADC1_Init 2 */

  /* USER CODE END ADC1_Init 2 */

}

/**
  * Enable DMA controller clock
  */
static void MX_DMA_Init(void)
{

  /* DMA controller clock enable */
  __HAL_RCC_DMA2_CLK_ENABLE();

  /* DMA interrupt init */
  /* DMA2_Stream0_IRQn interrupt configuration */
  HAL_NVIC_SetPriority(DMA2_Stream0_IRQn, 0, 0);
  HAL_NVIC_EnableIRQ(DMA2_Stream0_IRQn);

}

/**
  * @brief GPIO Initialization Function
  * @param None
  * @retval None
  */
static void MX_GPIO_Init(void)
{
  GPIO_InitTypeDef GPIO_InitStruct = {0};
  /* USER CODE BEGIN MX_GPIO_Init_1 */

  /* USER CODE END MX_GPIO_Init_1 */

  /* GPIO Ports Clock Enable */
  __HAL_RCC_GPIOC_CLK_ENABLE();
  __HAL_RCC_GPIOH_CLK_ENABLE();
  __HAL_RCC_GPIOA_CLK_ENABLE();

  /*Configure GPIO pin Output Level */
  HAL_GPIO_WritePin(LED_BLUE_GPIO_Port, LED_BLUE_Pin, GPIO_PIN_RESET);

  /*Configure GPIO pin Output Level */
  HAL_GPIO_WritePin(GPIOA, GPIO_PIN_9, GPIO_PIN_RESET);

  /*Configure GPIO pin : LED_BLUE_Pin */
  GPIO_InitStruct.Pin = LED_BLUE_Pin;
  GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
  GPIO_InitStruct.Pull = GPIO_NOPULL;
  GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_LOW;
  HAL_GPIO_Init(LED_BLUE_GPIO_Port, &GPIO_InitStruct);

  /*Configure GPIO pin : PA9 */
  GPIO_InitStruct.Pin = GPIO_PIN_9;
  GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
  GPIO_InitStruct.Pull = GPIO_NOPULL;
  GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_LOW;
  HAL_GPIO_Init(GPIOA, &GPIO_InitStruct);

  /* USER CODE BEGIN MX_GPIO_Init_2 */

  /* USER CODE END MX_GPIO_Init_2 */
}

/* USER CODE BEGIN 4 */

/* USER CODE END 4 */

/**
  * @brief  This function is executed in case of error occurrence.
  * @retval None
  */
void Error_Handler(void)
{
  /* USER CODE BEGIN Error_Handler_Debug */
  /* User can add his own implementation to report the HAL error return state */
  __disable_irq();
  while (1)
  {
  }
  /* USER CODE END Error_Handler_Debug */
}

#ifdef  USE_FULL_ASSERT
/**
  * @brief  Reports the name of the source file and the source line number
  *         where the assert_param error has occurred.
  * @param  file: pointer to the source file name
  * @param  line: assert_param error line source number
  * @retval None
  */
void assert_failed(uint8_t *file, uint32_t line)
{
  /* USER CODE BEGIN 6 */
  /* User can add his own implementation to report the file name and line number,
     ex: printf("Wrong parameters value: file %s on line %d\r\n", file, line) */
  /* USER CODE END 6 */
}
#endif /* USE_FULL_ASSERT */
