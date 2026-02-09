#ifndef __DDS__H__
#define __DDS__H__

#include <stdint.h>

typedef enum
{
  DDS_NONE = 0,
  DDS_OK,
  DDS_ERR
} e_dds_ststus;


typedef enum
{
  DDS_CHANNEL_1 = 1,
  DDS_CHANNEL_2,
  DDS_CHANNEL_3
} e_dds_channel_num;


typedef struct
{
  void (*send_data)(uint8_t *data, uint16_t len);
} t_dds_init;

e_dds_ststus DdsInit(t_dds_init * init);

e_dds_ststus DdsChannelOn(e_dds_channel_num chan_num);
e_dds_ststus DdsChannelOff(e_dds_channel_num chan_num);

e_dds_ststus DdsChannelSetFreq(e_dds_channel_num chan_num, uint32_t freq);
e_dds_ststus DdsChannelSetAmpl(e_dds_channel_num chan_num, uint32_t ampl);


#endif /* __DDS__H__ */
