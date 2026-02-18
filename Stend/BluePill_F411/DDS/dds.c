#include <string.h>
#include <stdbool.h>
#include <stdio.h>
#include "dds_defs.h"
#include "dds.h"

// ----------------------------------------------------------------------------
typedef struct
{
  bool is_init;
  t_dds_init init;

} t_dds_entity;
// ----------------------------------------------------------------------------
#define TX_DATA_BUF   50u
uint8_t TxDataBuf[TX_DATA_BUF];
t_dds_entity DdsEntity;
// ----------------------------------------------------------------------------
e_dds_ststus DdsInit(t_dds_init * init)
{
  e_dds_ststus res = DDS_OK;

  memcpy(&DdsEntity.init, init, sizeof(t_dds_init));
  DdsEntity.is_init = true;

  return res;
}
// ----------------------------------------------------------------------------
e_dds_ststus DdsChannelOn(e_dds_channel_num chan_num)
{
  uint8_t index = 0;
  e_dds_ststus res;

  memset(TxDataBuf, 0, TX_DATA_BUF);

  if(chan_num == DDS_CHANNEL_1)
  {
    index = sizeof(CMD_SET_WMN)-1;
    memcpy(TxDataBuf, CMD_SET_WMN, index);
    memcpy(&TxDataBuf[index++], "1", 1);
    memcpy(&TxDataBuf[index++], "\n", 1);
  }
  else if(chan_num == DDS_CHANNEL_2)
  {
    index = sizeof(CMD_SET_WFN)-1;
    memcpy(TxDataBuf, CMD_SET_WFN, index);
    memcpy(&TxDataBuf[index++], "1", 1);
    memcpy(&TxDataBuf[index++], "\n", 1);
  }
  else if(chan_num == DDS_CHANNEL_3)
  {
    index = sizeof(CMD_SET_TFN)-1;
    memcpy(TxDataBuf, CMD_SET_TFN, index);
    memcpy(&TxDataBuf[index++], "1", 1);
    memcpy(&TxDataBuf[index++], "\n", 1);
  }

  DdsEntity.init.send_data(TxDataBuf, index);

  return res;
}
// ----------------------------------------------------------------------------
e_dds_ststus DdsChannelOff(e_dds_channel_num chan_num)
{
  uint8_t index = 0;
  e_dds_ststus res;

  memset(TxDataBuf, 0, TX_DATA_BUF);

  if(chan_num == DDS_CHANNEL_1)
  {
    index = sizeof(CMD_SET_WMN)-1;
    memcpy(TxDataBuf, CMD_SET_WMN, index);
    memcpy(&TxDataBuf[index++], "0", 1);
    memcpy(&TxDataBuf[index++], "\n", 1);
  }
  else if(chan_num == DDS_CHANNEL_2)
  {
    index = sizeof(CMD_SET_WFN)-1;
    memcpy(TxDataBuf, CMD_SET_WFN, index);
    memcpy(&TxDataBuf[index++], "0", 1);
    memcpy(&TxDataBuf[index++], "\n", 1);
  }
  else if(chan_num == DDS_CHANNEL_3)
  {
    index = sizeof(CMD_SET_TFN)-1;
    memcpy(TxDataBuf, CMD_SET_TFN, index);
    memcpy(&TxDataBuf[index++], "0", 1);
    memcpy(&TxDataBuf[index++], "\n", 1);
  }

  DdsEntity.init.send_data(TxDataBuf, index);

  return res;
}
// ----------------------------------------------------------------------------
e_dds_ststus DdsChannelSetFreq(e_dds_channel_num chan_num, uint32_t freq)
{
  int index = 0;
  e_dds_ststus res;

  memset(TxDataBuf, 0, TX_DATA_BUF);

  if(chan_num == DDS_CHANNEL_1)
  {
    sprintf((char*)TxDataBuf, "%s%u\n", CMD_SET_WMF, freq);
  }
  else if(chan_num == DDS_CHANNEL_2)
  {
    sprintf((char*)TxDataBuf, "%s%u\n", CMD_SET_WFF, freq);
  }
  else if(chan_num == DDS_CHANNEL_3)
  {
    sprintf((char*)TxDataBuf, "%s%u\n", CMD_SET_TFF, freq);
  }

  index = strlen((char*)TxDataBuf);
  DdsEntity.init.send_data(TxDataBuf, index);

  return res;
}
// ----------------------------------------------------------------------------
e_dds_ststus DdsChannelSetAmpl(e_dds_channel_num chan_num, uint32_t ampl)
{
  int index = 0;
  e_dds_ststus res;

  memset(TxDataBuf, 0, TX_DATA_BUF);

  if(chan_num == DDS_CHANNEL_1)
  {
    sprintf((char*)TxDataBuf, "%s%u\n", CMD_SET_WMA, ampl);
  }
  else if(chan_num == DDS_CHANNEL_2)
  {
    sprintf((char*)TxDataBuf, "%s%u\n", CMD_SET_WFA, ampl);
  }
  else if(chan_num == DDS_CHANNEL_3)
  {
    sprintf((char*)TxDataBuf, "%s%u\n", CMD_SET_TFA, ampl);
  }

  index = strlen((char*)TxDataBuf);
  DdsEntity.init.send_data(TxDataBuf, index);

  return res;
}
// ----------------------------------------------------------------------------
