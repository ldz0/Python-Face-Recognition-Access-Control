/*******************************************************
ULN2003驱动5V减速步进电机程序
Target:STC89C52RC-40C
Crystal:12MHz
Author:战神单片机工作室
Platform:51&avr单片机最小系统板+ULN2003步进电机驱动套件
http://zsmcu.taobao.com   QQ:284083167
*******************************************************
接线方式:
IN1 ---- P00
IN2 ---- P01
IN3 ---- P02
IN4 ---- P03
+   ---- +5V
-   ---- GND
*********************/
#include<reg52.h>
#define uchar unsigned char
#define uint  unsigned int
#define MotorData P0                    //步进电机控制接口定义
uchar phasecw[4] ={0x08,0x04,0x02,0x01};//正转 电机导通相序 D-C-B-A
uchar phaseccw[4]={0x01,0x02,0x04,0x08};//反转 电机导通相序 A-B-C-D
//ms延时函数
void Delay_xms(uint x)
{
 uint i,j;
 for(i=0;i<x;i++)
  for(j=0;j<112;j++);
}
//顺时针转动
void MotorCW(void)
{
 uchar i;
 for(i=0;i<4;i++)
  {
   MotorData=phasecw[i];
   Delay_xms(4);//转速调节
  }
}
//逆时针转动
void MotorCCW(void)
{
 uchar i;
 for(i=0;i<4;i++)
  {
   MotorData=phaseccw[i];
   Delay_xms(4);//转速调节
  }
}
//停止转动
void MotorStop(void)
{
 MotorData=0x00;
}
//主函数
void main(void)
{
 uint i;
 Delay_xms(50);//等待系统稳定
 while(1)
 {
  for(i=0;i<500;i++)
  {
   MotorCW();   //顺时针转动
  } 
  MotorStop();  //停止转动
  Delay_xms(500);
  for(i=0;i<500;i++)
  {
   MotorCCW();  //逆时针转动
  } 
  MotorStop();  //停止转动
  Delay_xms(500);  
 }
}
