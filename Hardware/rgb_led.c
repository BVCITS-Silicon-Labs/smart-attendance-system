/*******************************************************************************
 * BRD2605A onboard RGB LED control
 ******************************************************************************/

#include "sl_si91x_rgb_led_instances.h"
#include "sl_si91x_rgb_led.h"

#ifndef RGB_LED
#define RGB_LED led_led0
#endif

void rgb_led_init(void)
{
  sl_si91x_simple_rgb_led_on(&RGB_LED);
  sl_si91x_simple_rgb_led_set_colour(&RGB_LED, 0x0000FF);
}

void rgb_led_set_red(void)
{
  sl_si91x_simple_rgb_led_on(&RGB_LED);
  sl_si91x_simple_rgb_led_set_colour(&RGB_LED, 0xFF0000);
}

void rgb_led_set_green(void)
{
  sl_si91x_simple_rgb_led_on(&RGB_LED);
  sl_si91x_simple_rgb_led_set_colour(&RGB_LED, 0x00FF00);
}

void rgb_led_set_blue(void)
{
  sl_si91x_simple_rgb_led_on(&RGB_LED);
  sl_si91x_simple_rgb_led_set_colour(&RGB_LED, 0x0000FF);
}

void rgb_led_off(void)
{
  sl_si91x_simple_rgb_led_off(&RGB_LED);
}

void rgb_led_process_action(void)
{
  /* No rainbow loop.
   * LED state is changed only by HTTP commands.
   */
}
