#ifndef RGB_LED_H
#define RGB_LED_H

void rgb_led_init(void);
void rgb_led_process_action(void);

void rgb_led_set_red(void);
void rgb_led_set_green(void);
void rgb_led_set_blue(void);
void rgb_led_off(void);

#endif
