#include "cli.h"
#include <string.h>
#include <stdio.h>
#include <stdlib.h>

static char rx_buffer[CLI_MAX_LINE_LEN];
static uint8_t rx_index = 0;
static volatile bool cmd_ready = false;

// --- Прототипы обработчиков команд ---
static void cmd_help(int argc, char *argv[]);
static void cmd_led(int argc, char *argv[]);
static void cmd_status(int argc, char *argv[]);

// --- Таблица всех доступных команд ---
static const cli_command_t cmd_table[] = {
    {"help",   "Show available commands",       cmd_help},
    {"led",    "Control LED: led <on|off>",     cmd_led},
    {"status", "Get system uptime and state",   cmd_status},
};

#define NUM_COMMANDS (sizeof(cmd_table) / sizeof(cli_command_t))

void cli_init(void) {
    rx_index = 0;
    cmd_ready = false;
    uart_send_str("\r\nMCU CLI Ready. Type 'help' for commands.\r\n> ");
}

// Эту функцию вызываем при получении каждого байта по UART
void cli_rx_char(char c) {
    if (cmd_ready) return; // Игнорируем ввод, пока предыдущая команда не обработана

    if (c == '\r' || c == '\n') {
        if (rx_index > 0) {
            rx_buffer[rx_index] = '\0';
            cmd_ready = true;
//            uart_send_str("\r\n");
        } else {
//            uart_send_str("\r\n> ");
        }
    } 
    else if (c == '\b' || c == 0x7F) { // Обработка Backspace
        if (rx_index > 0) {
            rx_index--;
            uart_send_str("\b \b"); // Стираем символ в терминале
        }
    } 
    else if (rx_index < (CLI_MAX_LINE_LEN - 1)) {
        // Принимаем только печатные ASCII символы
        if (c >= 32 && c <= 126) {
            rx_buffer[rx_index++] = c;
//            char echo[2] = {c, '\0'};
//            uart_send_str(echo); // Эхо-ответ пользователю
        }
    }
}

// Эту функцию крутим в main() -> while(1)
void cli_process(void) {
    if (!cmd_ready) return;

    char *argv[CLI_MAX_ARGS];
    int argc = 0;

    // Разбиваем строку по пробелам на токены
    char *token = strtok(rx_buffer, " ");
    while (token != NULL && argc < CLI_MAX_ARGS) {
        argv[argc++] = token;
        token = strtok(NULL, " ");
    }

    // Ищем команду в таблице
    if (argc > 0) {
        bool found = false;
        for (size_t i = 0; i < NUM_COMMANDS; i++) {
            if (strcmp(argv[0], cmd_table[i].name) == 0) {
                cmd_table[i].func(argc, argv);
                found = true;
                break;
            }
        }
        if (!found) {
            uart_send_str("Unknown command. Type 'help'.\r\n");
        }
    }

    // Сброс буфера и приглашение к следующему вводу
    rx_index = 0;
    cmd_ready = false;
    uart_send_str("> ");
}

// ================= РЕАЛИЗАЦИЯ КОМАНД =================

static void cmd_help(int argc, char *argv[]) {
    uart_send_str("Available commands:\r\n");
    for (size_t i = 0; i < NUM_COMMANDS; i++) {
        uart_send_str("  ");
        uart_send_str(cmd_table[i].name);
        uart_send_str("\t- ");
        uart_send_str(cmd_table[i].help);
        uart_send_str("\r\n");
    }
}

static void cmd_led(int argc, char *argv[]) {
    if (argc < 2) {
        uart_send_str("Usage: led <on|off>\r\n");
        return;
    }
    if (strcmp(argv[1], "on") == 0) {
        // HAL_GPIO_WritePin(LED_GPIO_Port, LED_Pin, GPIO_PIN_SET);
        uart_send_str("LED turned ON\r\n");
    } else if (strcmp(argv[1], "off") == 0) {
        // HAL_GPIO_WritePin(LED_GPIO_Port, LED_Pin, GPIO_PIN_RESET);
        uart_send_str("LED turned OFF\r\n");
    } else {
        uart_send_str("Invalid argument. Use 'on' or 'off'\r\n");
    }
}

static void cmd_status(int argc, char *argv[]) {
    char msg[64];
    // Пример форматированного вывода (можно подставить HAL_GetTick())
    snprintf(msg, sizeof(msg), "System OK. Args count: %d\r\n", argc);
    uart_send_str(msg);
}
