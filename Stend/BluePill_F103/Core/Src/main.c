/* USER CODE BEGIN Header */
/**
  ******************************************************************************
  * @file           : main.c
  * @brief          : Main program body
  ******************************************************************************
  * @attention
  *
  * Copyright (c) 2026 STMicroelectronics.
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

/* Private includes ----------------------------------------------------------*/
/* USER CODE BEGIN Includes */
#include <stdbool.h>
#include <stdio.h>
#include <string.h>
#include "../../DDS/dds.h"
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
ADC_HandleTypeDef hadc2;
DMA_HandleTypeDef hdma_adc1;

UART_HandleTypeDef huart1;
UART_HandleTypeDef huart3;

/* USER CODE BEGIN PV */
#define AMPLITUDE   3.30 // Volt
#define FREQ_START  100
#define FREQ_STOP   40000
#define FREQ_STEP   100

#define ADC_BIG_DATA_BUF_SIZE    4285 // 1742u // 30468u

typedef enum
{
  MODE_PGM_START,
  MODE_DDS_ON,
  MODE_ADC_COLLECTING,
  MODE_ADC_COLLECT_STOP,
  MODE_USB_TX_START,
  MODE_USB_TX,
  MODE_STOP
} work_modes_t;

// номера АЦП каналов в массиве AdcDmaDataBuf
//enum
//{
//  ADC_IN_0 = 0,
//  ADC_IN_1 = 1,
//  ADC_DATA_BUF_SIZE
//};

//typedef struct
//{
//  uint16_t data[ADC_DATA_BUF_SIZE];
//} adc_channels_array_t;

// структура массива данных
//typedef struct
//{
//  adc_channels_array_t channels[ADC_BIG_DATA_BUF_SIZE];
//  uint32_t channel_index;
//} adc_big_array_t;

uint32_t DataBuf[ADC_BIG_DATA_BUF_SIZE];

work_modes_t WorkMode;
uint32_t DataCollectTime;
//volatile uint16_t DmaData[ADC_DATA_BUF_SIZE];
//volatile adc_big_array_t AdcBigDataBuf;

bool DataCollecionIsStarted = false;
/* USER CODE END PV */

/* Private function prototypes -----------------------------------------------*/
void SystemClock_Config(void);
static void MX_GPIO_Init(void);
static void MX_DMA_Init(void);
static void MX_ADC1_Init(void);
static void MX_USART1_UART_Init(void);
static void MX_USART3_UART_Init(void);
static void MX_ADC2_Init(void);
/* USER CODE BEGIN PFP */
// ----------------------------------------------------------------------------
// старт преобразования каналов АЦП
void AdcStartConversion(void)
{
  HAL_ADC_Start(&hadc2);
  HAL_ADCEx_MultiModeStart_DMA(&hadc1, DataBuf, ADC_BIG_DATA_BUF_SIZE);
//  HAL_ADC_Start_DMA(&hadc1, (uint32_t*)DmaData, ADC_DATA_BUF_SIZE);
}
// ----------------------------------------------------------------------------
// запуск заполнения массива данными
void StartDataCollection(void)
{
  if(DataCollecionIsStarted == true)
    return;

  DataCollecionIsStarted = true;
//  AdcBigDataBuf.channel_index = 0;

  DataCollectTime = HAL_GetTick();
  AdcStartConversion();
}
// ----------------------------------------------------------------------------
//void HAL_ADC_ConvHalfCpltCallback(ADC_HandleTypeDef* hadc)
//{
////  AdcStartConversion();
//  HAL_GPIO_TogglePin(GPIOA, GPIO_PIN_9);
//}
void HAL_ADC_ConvCpltCallback(ADC_HandleTypeDef *hadc)
{
  HAL_ADCEx_MultiModeStop_DMA(&hadc1);
//  HAL_ADC_Stop_DMA(&hadc1);
  if(DataCollecionIsStarted)
    AdcStartConversion();

//  AdcBigDataBuf.channels[AdcBigDataBuf.channel_index].data[0] = DmaData[0];
//  AdcBigDataBuf.channels[AdcBigDataBuf.channel_index].data[1] = DmaData[1];

//  AdcBigDataBuf.channel_index++;
//  if(AdcBigDataBuf.channel_index == ADC_BIG_DATA_BUF_SIZE)
  {
    DataCollectTime = HAL_GetTick() - DataCollectTime;
    DataCollecionIsStarted = false;
  }
  HAL_GPIO_TogglePin(GPIOA, GPIO_PIN_9);
}
// ----------------------------------------------------------------------------
void UartSendData(uint8_t *data, uint16_t len)
{
  HAL_UART_Transmit(&huart1, data, len, 100);
  HAL_Delay(200);
}
// ----------------------------------------------------------------------------
void DdsGenSetup(void)
{
  t_dds_init init;

  init.send_data = UartSendData;

  DdsInit(&init);

  DdsChannelOff(DDS_CHANNEL_1);
  DdsChannelOff(DDS_CHANNEL_2);
  DdsChannelOff(DDS_CHANNEL_3);
}
// ----------------------------------------------------------------------------
void LedSwitch(bool on)
{ HAL_GPIO_WritePin(LED_GPIO_Port, LED_Pin, (on)?(GPIO_PIN_RESET):(GPIO_PIN_SET)); }
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
  uint32_t freq = FREQ_START;
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
  MX_USART1_UART_Init();
  MX_USART3_UART_Init();
  MX_ADC2_Init();
  /* USER CODE BEGIN 2 */
  DdsGenSetup();

  WorkMode = MODE_PGM_START;

  sprintf(usb_tx_buf, "Program start.\r\n");
  HAL_UART_Transmit(&huart3, (uint8_t*)usb_tx_buf, strlen(usb_tx_buf), 100);
  /* USER CODE END 2 */

  /* Infinite loop */
  /* USER CODE BEGIN WHILE */
  while(1)
  {
    switch(WorkMode)
    {
      case MODE_PGM_START:
        LedSwitch(true);
        if(HAL_GPIO_ReadPin(KEY_GPIO_Port, KEY_Pin) == GPIO_PIN_RESET)
        {
          LedSwitch(false);
          HAL_Delay(500);
          WorkMode = MODE_DDS_ON;
        }
        break;
      case MODE_DDS_ON:
          DdsChannelOn(DDS_CHANNEL_1);
//          DdsChannelSetAmpl(DDS_CHANNEL_1, AMPLITUDE);
          DdsChannelSetFreq(DDS_CHANNEL_1, freq);

          HAL_Delay(100); // ждём чтобы генератор нормально включился
          StartDataCollection();
          LedSwitch(false);
          WorkMode = MODE_ADC_COLLECTING;
        break;
      case MODE_ADC_COLLECTING:
        if(!DataCollecionIsStarted)
        {
          DdsChannelOff(DDS_CHANNEL_1);
          WorkMode = MODE_ADC_COLLECT_STOP;
        }
        break;
      case MODE_ADC_COLLECT_STOP:
        usb_tx_data_index = 0;
        LedSwitch(false);
        WorkMode = MODE_USB_TX_START;
        break;
      case MODE_USB_TX_START:
        usb_tx_data_index = 0;
        sprintf(usb_tx_buf, "{\"freq\":%d,\"data\":[", freq);
//        while( CDC_Transmit_FS((uint8_t*)usb_tx_buf, strlen(usb_tx_buf)) != USBD_OK){}
        HAL_UART_Transmit(&huart3, (uint8_t*)usb_tx_buf, strlen(usb_tx_buf), 100);
        WorkMode = MODE_USB_TX;
        break;
      case MODE_USB_TX:
        LedSwitch(true);

        if( usb_tx_data_index == 0)
        {
          sprintf(usb_tx_buf, "[%d,%d]",
            (DataBuf[usb_tx_data_index] & 0xFFFF), // AdcBigDataBuf.channels[usb_tx_data_index].data[ADC_IN_0],
            (DataBuf[usb_tx_data_index] >> 16)); // AdcBigDataBuf.channels[usb_tx_data_index].data[ADC_IN_1]);
//            AdcBigDataBuf.channels[usb_tx_data_index].data[ADC_IN_0],
//            AdcBigDataBuf.channels[usb_tx_data_index].data[ADC_IN_1]);
        }
        else
        {
          sprintf(usb_tx_buf, ",[%d,%d]",
            (DataBuf[usb_tx_data_index] & 0xFFFF),
            (DataBuf[usb_tx_data_index] >> 16));
//            AdcBigDataBuf.channels[usb_tx_data_index].data[ADC_IN_0],
//            AdcBigDataBuf.channels[usb_tx_data_index].data[ADC_IN_1]);
        }

//        while( CDC_Transmit_FS((uint8_t*)usb_tx_buf, strlen(usb_tx_buf)) != USBD_OK){}
        HAL_UART_Transmit(&huart3, (uint8_t*)usb_tx_buf, strlen(usb_tx_buf), 100);
        usb_tx_data_index++;
        if(usb_tx_data_index >= ADC_BIG_DATA_BUF_SIZE)
        {
          usb_tx_data_index = 0;

//          USBD_CDC_HandleTypeDef *hcdc = (USBD_CDC_HandleTypeDef*)hUsbDeviceFS.pClassData;
//          while(hcdc->TxState != 0) {}
          sprintf(usb_tx_buf, "]}\r\n");
//          CDC_Transmit_FS((uint8_t*)usb_tx_buf, strlen(usb_tx_buf));
          HAL_UART_Transmit(&huart3, (uint8_t*)usb_tx_buf, strlen(usb_tx_buf), 100);
          if(freq < FREQ_STOP)
          {
            freq += FREQ_STEP;
            WorkMode = MODE_DDS_ON;
          }
          else
          {
            freq = FREQ_START;
            WorkMode = MODE_STOP;
          }
        }


//        sprintf(usb_tx_buf, "{\"TIME_STAMP\":%d,\"freq\":%d,\"Ch0\":%d,\"Ch1\":%d}\r\n",
//                usb_tx_data_index,
//                freq,
//                AdcBigDataBuf.channels[usb_tx_data_index].data[ADC_IN_0],
//                AdcBigDataBuf.channels[usb_tx_data_index].data[ADC_IN_1]);
//        if( CDC_Transmit_FS((uint8_t*)usb_tx_buf, strlen(usb_tx_buf)) == USBD_OK)
//        {
//          usb_tx_data_index++;
//          if(usb_tx_data_index >= ADC_BIG_DATA_BUF_SIZE)
//          {
//            usb_tx_data_index = 0;

//            USBD_CDC_HandleTypeDef *hcdc = (USBD_CDC_HandleTypeDef*)hUsbDeviceFS.pClassData;
//            while(hcdc->TxState != 0) {}
//            sprintf(usb_tx_buf, "---------------------------------------\r\n");
//            CDC_Transmit_FS((uint8_t*)usb_tx_buf, strlen(usb_tx_buf));

//            if(freq < FREQ_STOP)
//            {
//              freq += FREQ_STEP;
//              WorkMode = MODE_DDS_ON;
//            }
//            else
//            {
//              freq = FREQ_START;
//              WorkMode = MODE_STOP;
//            }
//          }
//        }
        break;
      case MODE_STOP:
        WorkMode = MODE_PGM_START;
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
  RCC_PeriphCLKInitTypeDef PeriphClkInit = {0};

  /** Initializes the RCC Oscillators according to the specified parameters
  * in the RCC_OscInitTypeDef structure.
  */
  RCC_OscInitStruct.OscillatorType = RCC_OSCILLATORTYPE_HSE;
  RCC_OscInitStruct.HSEState = RCC_HSE_ON;
  RCC_OscInitStruct.HSEPredivValue = RCC_HSE_PREDIV_DIV1;
  RCC_OscInitStruct.HSIState = RCC_HSI_ON;
  RCC_OscInitStruct.PLL.PLLState = RCC_PLL_ON;
  RCC_OscInitStruct.PLL.PLLSource = RCC_PLLSOURCE_HSE;
  RCC_OscInitStruct.PLL.PLLMUL = RCC_PLL_MUL9;
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
  RCC_ClkInitStruct.APB2CLKDivider = RCC_HCLK_DIV2;

  if (HAL_RCC_ClockConfig(&RCC_ClkInitStruct, FLASH_LATENCY_2) != HAL_OK)
  {
    Error_Handler();
  }
  PeriphClkInit.PeriphClockSelection = RCC_PERIPHCLK_ADC;
  PeriphClkInit.AdcClockSelection = RCC_ADCPCLK2_DIV6;
  if (HAL_RCCEx_PeriphCLKConfig(&PeriphClkInit) != HAL_OK)
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

  ADC_MultiModeTypeDef multimode = {0};
  ADC_ChannelConfTypeDef sConfig = {0};

  /* USER CODE BEGIN ADC1_Init 1 */

  /* USER CODE END ADC1_Init 1 */

  /** Common config
  */
  hadc1.Instance = ADC1;
  hadc1.Init.ScanConvMode = ADC_SCAN_DISABLE;
  hadc1.Init.ContinuousConvMode = ENABLE;
  hadc1.Init.DiscontinuousConvMode = DISABLE;
  hadc1.Init.ExternalTrigConv = ADC_SOFTWARE_START;
  hadc1.Init.DataAlign = ADC_DATAALIGN_RIGHT;
  hadc1.Init.NbrOfConversion = 1;
  if (HAL_ADC_Init(&hadc1) != HAL_OK)
  {
    Error_Handler();
  }

  /** Configure the ADC multi-mode
  */
  multimode.Mode = ADC_DUALMODE_REGSIMULT;
  if (HAL_ADCEx_MultiModeConfigChannel(&hadc1, &multimode) != HAL_OK)
  {
    Error_Handler();
  }

  /** Configure Regular Channel
  */
  sConfig.Channel = ADC_CHANNEL_2;
  sConfig.Rank = ADC_REGULAR_RANK_1;
  sConfig.SamplingTime = ADC_SAMPLETIME_1CYCLE_5;
  if (HAL_ADC_ConfigChannel(&hadc1, &sConfig) != HAL_OK)
  {
    Error_Handler();
  }
  /* USER CODE BEGIN ADC1_Init 2 */

  /* USER CODE END ADC1_Init 2 */

}

/**
  * @brief ADC2 Initialization Function
  * @param None
  * @retval None
  */
static void MX_ADC2_Init(void)
{

  /* USER CODE BEGIN ADC2_Init 0 */

  /* USER CODE END ADC2_Init 0 */

  ADC_ChannelConfTypeDef sConfig = {0};

  /* USER CODE BEGIN ADC2_Init 1 */

  /* USER CODE END ADC2_Init 1 */

  /** Common config
  */
  hadc2.Instance = ADC2;
  hadc2.Init.ScanConvMode = ADC_SCAN_DISABLE;
  hadc2.Init.ContinuousConvMode = ENABLE;
  hadc2.Init.DiscontinuousConvMode = DISABLE;
  hadc2.Init.ExternalTrigConv = ADC_SOFTWARE_START;
  hadc2.Init.DataAlign = ADC_DATAALIGN_RIGHT;
  hadc2.Init.NbrOfConversion = 1;
  if (HAL_ADC_Init(&hadc2) != HAL_OK)
  {
    Error_Handler();
  }

  /** Configure Regular Channel
  */
  sConfig.Channel = ADC_CHANNEL_3;
  sConfig.Rank = ADC_REGULAR_RANK_1;
  sConfig.SamplingTime = ADC_SAMPLETIME_1CYCLE_5;
  if (HAL_ADC_ConfigChannel(&hadc2, &sConfig) != HAL_OK)
  {
    Error_Handler();
  }
  /* USER CODE BEGIN ADC2_Init 2 */

  /* USER CODE END ADC2_Init 2 */

}

/**
  * @brief USART1 Initialization Function
  * @param None
  * @retval None
  */
static void MX_USART1_UART_Init(void)
{

  /* USER CODE BEGIN USART1_Init 0 */

  /* USER CODE END USART1_Init 0 */

  /* USER CODE BEGIN USART1_Init 1 */

  /* USER CODE END USART1_Init 1 */
  huart1.Instance = USART1;
  huart1.Init.BaudRate = 115200;
  huart1.Init.WordLength = UART_WORDLENGTH_8B;
  huart1.Init.StopBits = UART_STOPBITS_1;
  huart1.Init.Parity = UART_PARITY_NONE;
  huart1.Init.Mode = UART_MODE_TX_RX;
  huart1.Init.HwFlowCtl = UART_HWCONTROL_NONE;
  huart1.Init.OverSampling = UART_OVERSAMPLING_16;
  if (HAL_UART_Init(&huart1) != HAL_OK)
  {
    Error_Handler();
  }
  /* USER CODE BEGIN USART1_Init 2 */

  /* USER CODE END USART1_Init 2 */

}

/**
  * @brief USART3 Initialization Function
  * @param None
  * @retval None
  */
static void MX_USART3_UART_Init(void)
{

  /* USER CODE BEGIN USART3_Init 0 */

  /* USER CODE END USART3_Init 0 */

  /* USER CODE BEGIN USART3_Init 1 */

  /* USER CODE END USART3_Init 1 */
  huart3.Instance = USART3;
  huart3.Init.BaudRate = 115200;
  huart3.Init.WordLength = UART_WORDLENGTH_8B;
  huart3.Init.StopBits = UART_STOPBITS_1;
  huart3.Init.Parity = UART_PARITY_NONE;
  huart3.Init.Mode = UART_MODE_TX_RX;
  huart3.Init.HwFlowCtl = UART_HWCONTROL_NONE;
  huart3.Init.OverSampling = UART_OVERSAMPLING_16;
  if (HAL_UART_Init(&huart3) != HAL_OK)
  {
    Error_Handler();
  }
  /* USER CODE BEGIN USART3_Init 2 */

  /* USER CODE END USART3_Init 2 */

}

/**
  * Enable DMA controller clock
  */
static void MX_DMA_Init(void)
{

  /* DMA controller clock enable */
  __HAL_RCC_DMA1_CLK_ENABLE();

  /* DMA interrupt init */
  /* DMA1_Channel1_IRQn interrupt configuration */
  HAL_NVIC_SetPriority(DMA1_Channel1_IRQn, 0, 0);
  HAL_NVIC_EnableIRQ(DMA1_Channel1_IRQn);

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
  __HAL_RCC_GPIOD_CLK_ENABLE();
  __HAL_RCC_GPIOA_CLK_ENABLE();
  __HAL_RCC_GPIOB_CLK_ENABLE();

  /*Configure GPIO pin Output Level */
  HAL_GPIO_WritePin(LED_GPIO_Port, LED_Pin, GPIO_PIN_RESET);

  /*Configure GPIO pin : LED_Pin */
  GPIO_InitStruct.Pin = LED_Pin;
  GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
  GPIO_InitStruct.Pull = GPIO_NOPULL;
  GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_LOW;
  HAL_GPIO_Init(LED_GPIO_Port, &GPIO_InitStruct);

  /*Configure GPIO pin : KEY_Pin */
  GPIO_InitStruct.Pin = KEY_Pin;
  GPIO_InitStruct.Mode = GPIO_MODE_INPUT;
  GPIO_InitStruct.Pull = GPIO_PULLUP;
  HAL_GPIO_Init(KEY_GPIO_Port, &GPIO_InitStruct);

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
