#include <math.h>
#include "dds_synthesis.h"

// настройки таймера
static double Fapb1;       // частота тактирования таймера
static uint16_t Prescaler; // 16bit
static uint16_t Period;    // Auto reload register ARR 16bit
static double Fsample;   // 1312500 частота дискретизации = частота вызова таймера

uint32_t UINT32_MAX_VALUE; // UINT32_MAX = 0xFFFFFFFF + 1; // 4 294 967 295 + 1 = 4 294 967 296

#define M_PI      3.1415926f
#define LUT_SIZE  1024u      // размер таблицы синуса
uint16_t SINE_LUT[LUT_SIZE]; // таблица синуса

// переменные DDS
volatile uint32_t PHASE_ACCUMULATOR; // 32-битный аккумулятор фазы
volatile uint32_t PHASE_INCREMENT;   // Шаг фазы (определяет частоту)

static void (*DAC_SetValueCb)(uint16_t);
// ----------------------------------------------------------------------------
//    ''' генерация таблицы периода синуса '''
static void SinusDataGenerate(uint16_t *sine_lut, uint16_t lut_size)
{
  uint16_t new_value;

  for(int i = 0; i < lut_size; ++i)
  {
    sine_lut[i] = (uint16_t)((sinf(2.0f * M_PI * i / lut_size) + 1.0f) * 2047.5f);
  }
}
// ----------------------------------------------------------------------------
void DdsSetFreq(uint32_t target_freq)
{
  // Формула шага фазы для 32-битного аккумулятора:
//  PHASE_INCREMENT = (uint32_t)((target_freq * 4294967296.0) / Fsample);
  PHASE_INCREMENT = (uint32_t)(((float)target_freq * 4294967296.0f) / Fsample);
}
// ----------------------------------------------------------------------------
void DDS_Init(dds_init_t * init)
{
  Fapb1     = init->Fapb1;
  Prescaler = init->Prescaler;
  Period    = init->Period;

  DAC_SetValueCb = init->dac_set_value_cb;

  Fsample   = Fapb1 / (Period + 1);

  PHASE_ACCUMULATOR = 0;
  PHASE_INCREMENT   = 0;

  DdsSetFreq(init->freq);

  SinusDataGenerate(SINE_LUT, LUT_SIZE);
}
// ----------------------------------------------------------------------------
void DdsTimerIrqCallback(void)
{
  PHASE_ACCUMULATOR += PHASE_INCREMENT;
  
  uint32_t index = PHASE_ACCUMULATOR >> 22;
  
  DAC_SetValueCb(SINE_LUT[index]);
}
// ----------------------------------------------------------------------------
