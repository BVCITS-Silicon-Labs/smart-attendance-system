/*
 * Face Attendance LED Gate
 * Silicon Labs SiWG917 + BRD2605A
 *
 * LED:
 * BLUE  = Normal / Idle
 * GREEN = Correct / Recognized person
 * RED   = Unknown / Wrong person
 *
 * HTTP endpoints:
 * GET /health?key=<API_KEY>
 * GET /led?color=red&key=<API_KEY>
 * GET /led?color=green&key=<API_KEY>
 * GET /led?color=blue&key=<API_KEY>
 */

#include <stdio.h>
#include <string.h>
#include <stdint.h>

#include "app.h"
#include "rgb_led.h"

#include "sl_status.h"
#include "sl_net.h"
#include "sl_http_server.h"


/* =========================================================
 * CONFIGURATION
 * ========================================================= */

#define HTTP_PORT 80

#define API_KEY "my-student-attendance-bvc@123"


/* =========================================================
 * HTTP SERVER
 * ========================================================= */

static sl_http_server_t http_server;


/* =========================================================
 * QUERY PARAMETER HELPER
 * ========================================================= */

static const char *get_query_value(
    sl_http_server_request_t *request,
    const char *name)
{
    uint16_t i;

    if (request == NULL || name == NULL) {
        return NULL;
    }

    for (i = 0;
         i < request->uri.query_parameter_count;
         i++)
    {
        if (request->uri.query_parameters[i].query != NULL &&
            request->uri.query_parameters[i].value != NULL)
        {
            if (strcmp(
                    request->uri.query_parameters[i].query,
                    name) == 0)
            {
                return request->uri.query_parameters[i].value;
            }
        }
    }

    return NULL;
}


/* =========================================================
 * JSON RESPONSE
 * ========================================================= */

static sl_status_t send_json(
    sl_http_server_t *handle,
    uint16_t code,
    const char *json)
{
    sl_http_server_response_t response;

    memset(&response, 0, sizeof(response));

    response.response_code =
        (sl_http_response_code_t)code;

    response.content_type = "application/json";

    response.headers = NULL;
    response.header_count = 0;

    response.data =
        (uint8_t *)json;

    response.current_data_length =
        (uint32_t)strlen(json);

    response.expected_data_length =
        (uint32_t)strlen(json);

    return sl_http_server_send_response(
        handle,
        &response);
}


/* =========================================================
 * HTTP REQUEST HANDLER
 * ========================================================= */

static sl_status_t http_request_handler(
    sl_http_server_t *handle,
    sl_http_server_request_t *request)
{
    const char *key;
    const char *color;


    /* -----------------------------------------------------
     * Validate request
     * ----------------------------------------------------- */

    if (request == NULL ||
        request->uri.path == NULL)
    {
        return send_json(
            handle,
            400,
            "{\"success\":false,"
            "\"message\":\"Bad request\"}");
    }


    /* -----------------------------------------------------
     * Check API key
     * ----------------------------------------------------- */

    key = get_query_value(
        request,
        "key");

    if (key == NULL ||
        strcmp(key, API_KEY) != 0)
    {
        return send_json(
            handle,
            401,
            "{\"success\":false,"
            "\"message\":\"Unauthorized\"}");
    }


    /* =====================================================
     * HEALTH
     * ===================================================== */

    if (strcmp(
            request->uri.path,
            "/health") == 0)
    {
        return send_json(
            handle,
            200,
            "{\"success\":true,"
            "\"device\":\"SIWG917-BRD2605A\","
            "\"status\":\"online\"}");
    }


    /* =====================================================
     * LED
     * ===================================================== */

    if (strcmp(
            request->uri.path,
            "/led") == 0)
    {
        color = get_query_value(
            request,
            "color");


        /* -------------------------------------------------
         * No color
         * ------------------------------------------------- */

        if (color == NULL)
        {
            return send_json(
                handle,
                400,
                "{\"success\":false,"
                "\"message\":\"color is required\"}");
        }


        /* -------------------------------------------------
         * RED
         * ------------------------------------------------- */

        if (strcmp(
                color,
                "red") == 0)
        {
            rgb_led_set_red();

            printf(
                "LED COMMAND: RED\r\n");

            return send_json(
                handle,
                200,
                "{\"success\":true,"
                "\"color\":\"red\"}");
        }


        /* -------------------------------------------------
         * GREEN
         * ------------------------------------------------- */

        if (strcmp(
                color,
                "green") == 0)
        {
            rgb_led_set_green();

            printf(
                "LED COMMAND: GREEN\r\n");

            return send_json(
                handle,
                200,
                "{\"success\":true,"
                "\"color\":\"green\"}");
        }


        /* -------------------------------------------------
         * BLUE
         * ------------------------------------------------- */

        if (strcmp(
                color,
                "blue") == 0)
        {
            rgb_led_set_blue();

            printf(
                "LED COMMAND: BLUE\r\n");

            return send_json(
                handle,
                200,
                "{\"success\":true,"
                "\"color\":\"blue\"}");
        }


        /* -------------------------------------------------
         * Invalid color
         * ------------------------------------------------- */

        return send_json(
            handle,
            400,
            "{\"success\":false,"
            "\"message\":\"invalid color\"}");
    }


    /* =====================================================
     * UNKNOWN URL
     * ===================================================== */

    return send_json(
        handle,
        404,
        "{\"success\":false,"
        "\"message\":\"not found\"}");
}


/* =========================================================
 * HTTP HANDLERS
 * ========================================================= */

static sl_http_server_handler_t handlers[] =
{
    {
        .uri = "/health",
        .handler = http_request_handler
    },

    {
        .uri = "/led",
        .handler = http_request_handler
    }
};


/* =========================================================
 * HTTP CONFIGURATION
 * ========================================================= */

static sl_http_server_config_t http_config =
{
    .port = HTTP_PORT,

    .handlers_list = handlers,

    .handlers_count = 2,

    .default_handler = http_request_handler,

    .client_idle_time = 30
};


/* =========================================================
 * PRINT IP ADDRESS
 * ========================================================= */

static void print_board_ip_address(void)
{
    sl_status_t status;

    sl_net_interface_info_t interface_info;


    memset(
        &interface_info,
        0,
        sizeof(interface_info));


    status = sl_net_get_interface_info(
        SL_NET_WIFI_CLIENT_INTERFACE,
        &interface_info);


    if (status == SL_STATUS_OK)
    {
        printf(
            "\r\n"
            "========================================\r\n");

        printf(
            "SiWG917 IPv4 Address: %u.%u.%u.%u\r\n",
            interface_info.ipv4_address.bytes[0],
            interface_info.ipv4_address.bytes[1],
            interface_info.ipv4_address.bytes[2],
            interface_info.ipv4_address.bytes[3]);

        printf(
            "========================================\r\n");
    }
    else
    {
        printf(
            "IP ADDRESS ERROR: 0x%lx\r\n",
            (unsigned long)status);
    }
}


/* =========================================================
 * APPLICATION INIT
 * ========================================================= */

void app_init(void)
{
    sl_status_t status;


    /* =====================================================
     * START MESSAGE
     * ===================================================== */

    printf(
        "\r\n\r\n"
        "***************************************\r\n");

    printf(
        "SiWG917 FACE ATTENDANCE APPLICATION\r\n");

    printf(
        "BRD2605A\r\n");

    printf(
        "APPLICATION STARTED\r\n");

    printf(
        "***************************************\r\n");


    /* =====================================================
     * RGB LED INITIALIZATION
     * ===================================================== */

    rgb_led_init();


    /*
     * Normal condition = BLUE
     */

    rgb_led_set_blue();


    printf(
        "RGB LED initialized\r\n");

    printf(
        "NORMAL STATE: BLUE\r\n");


    /* =====================================================
     * INITIALIZE NETWORK
     * ===================================================== */

    printf(
        "Initializing Wi-Fi...\r\n");


    status = sl_net_init(
        SL_NET_WIFI_CLIENT_INTERFACE,
        NULL,
        NULL,
        NULL);


    if (status != SL_STATUS_OK)
    {
        printf(
            "ERROR: sl_net_init failed\r\n");

        printf(
            "STATUS: 0x%lx\r\n",
            (unsigned long)status);

        return;
    }


    printf(
        "Wi-Fi interface initialized\r\n");


    /* =====================================================
     * CONNECT TO WIFI
     *
     * SSID and password come from:
     *
     * sl_net_default_values.h
     * ===================================================== */

    printf(
        "Connecting to Wi-Fi...\r\n");


    status = sl_net_up(
        SL_NET_WIFI_CLIENT_INTERFACE,
        SL_NET_DEFAULT_WIFI_CLIENT_PROFILE_ID);


    if (status != SL_STATUS_OK)
    {
        printf(
            "ERROR: Wi-Fi connection failed\r\n");

        printf(
            "STATUS: 0x%lx\r\n",
            (unsigned long)status);

        /*
         * RED indicates Wi-Fi/application error.
         */

        rgb_led_set_red();

        return;
    }


    printf(
        "Wi-Fi connected successfully!\r\n");


    /* =====================================================
     * GET IP ADDRESS
     * ===================================================== */

    print_board_ip_address();


    /* =====================================================
     * BIND HTTP SERVER
     * ===================================================== */

    printf(
        "Binding HTTP server...\r\n");


    status =
        sl_http_server_bind_interface(
            SL_NET_WIFI_CLIENT_INTERFACE);


    if (status != SL_STATUS_OK)
    {
        printf(
            "ERROR: HTTP bind failed\r\n");

        printf(
            "STATUS: 0x%lx\r\n",
            (unsigned long)status);

        rgb_led_set_red();

        return;
    }


    printf(
        "HTTP interface bind successful\r\n");


    /* =====================================================
     * INITIALIZE HTTP SERVER
     * ===================================================== */

    printf(
        "Initializing HTTP server...\r\n");


    status =
        sl_http_server_init(
            &http_server,
            &http_config);


    if (status != SL_STATUS_OK)
    {
        printf(
            "ERROR: HTTP server init failed\r\n");

        printf(
            "STATUS: 0x%lx\r\n",
            (unsigned long)status);

        rgb_led_set_red();

        return;
    }


    printf(
        "HTTP server initialized\r\n");


    /* =====================================================
     * START HTTP SERVER
     * ===================================================== */

    printf(
        "Starting HTTP server...\r\n");


    status =
        sl_http_server_start(
            &http_server);


    if (status != SL_STATUS_OK)
    {
        printf(
            "ERROR: HTTP server start failed\r\n");

        printf(
            "STATUS: 0x%lx\r\n",
            (unsigned long)status);

        rgb_led_set_red();

        return;
    }


    /* =====================================================
     * SERVER READY
     * ===================================================== */

    printf(
        "\r\n"
        "========================================\r\n");

    printf(
        "HTTP SERVER STARTED\r\n");

    printf(
        "PORT: %d\r\n",
        HTTP_PORT);

    printf(
        "DEVICE: SiWG917 + BRD2605A\r\n");

    printf(
        "STATUS: ONLINE\r\n");

    printf(
        "========================================\r\n");


    printf(
        "Health:\r\n");

    printf(
        "/health?key=<API_KEY>\r\n");


    printf(
        "\r\nLED TEST URLs:\r\n");

    printf(
        "/led?color=red&key=<API_KEY>\r\n");

    printf(
        "/led?color=green&key=<API_KEY>\r\n");

    printf(
        "/led?color=blue&key=<API_KEY>\r\n");


    printf(
        "\r\n"
        "FACE ATTENDANCE GATE READY\r\n");


    /*
     * Keep normal state BLUE.
     */

    rgb_led_set_blue();
}


/* =========================================================
 * APPLICATION PROCESS
 * ========================================================= */

void app_process_action(void)
{
    /*
     * HTTP server runs in its own thread.
     *
     * No periodic processing required here.
     */
}