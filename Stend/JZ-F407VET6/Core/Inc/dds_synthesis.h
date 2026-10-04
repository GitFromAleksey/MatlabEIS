#ifndef DDS_SYNTHESIS_H
#define DDS_SYNTHESIS_H

#ifdef __cplusplus
extern "C" {
#endif

#include "stdint.h"


typedef struct
{
  double   Fapb1;        // частота тактирования таймера
  uint16_t Prescaler;    // делитель частоты таймера
  uint16_t Period;       // Auto reload register ARR
  uint32_t freq;
  void (*dac_set_value_cb)(uint16_t);

} dds_init_t;


void DDS_Init(dds_init_t *);
void DdsSetFreq(uint32_t);
void DdsTimerIrqCallback(void);


#ifdef __cplusplus
}
#endif

#endif /* DDS_SYNTHESIS_H */
