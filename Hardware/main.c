/***************************************************************************//**
 * @file main.c
 * @brief Main function for SiWG917 RTOS application.
 ******************************************************************************/

#include "sl_main_init.h"
#include "sl_main_kernel.h"

int main(void)
{
  /*
   * IMPORTANT:
   *
   * For RTOS applications, sl_main_init() and
   * sl_main_kernel_start() are handled by the
   * Silicon Labs main retarget.
   *
   * This main() runs from the FreeRTOS start task.
   */

  /*
   * Initialize the second stage:
   *
   * - Platform
   * - Drivers
   * - IO Stream / VCOM
   * - Services
   * - Wi-Fi/network stack
   * - Internal components
   */
  sl_main_second_stage_init();


  /*
   * Start user application.
   *
   * This calls your app.c:
   *
   * app_init()
   *
   * Inside app_init():
   * - RGB LED initialization
   * - Wi-Fi connection
   * - IP address
   * - HTTP server
   */
  app_init();


  /*
   * Keep the start task alive.
   *
   * HTTP server and Wi-Fi run through
   * their own RTOS tasks.
   */
  while (1)
  {
    /*
     * Nothing periodic required here.
     */
  }
}