#ifndef CLI_H
#define CLI_H

#include <stdint.h>
#include <stdbool.h>

#define CLI_MAX_LINE_LEN  64  // Максимальная длина вводимой строки
#define CLI_MAX_ARGS      9   // Максимальное количество аргументов

// Тип функции-обработчика команды
typedef void (*cli_cmd_func_t)(int argc, char *argv[]);

// Структура описания команды
typedef struct {
    const char *name;        // Имя команды (например, "led")
    const char *help;        // Краткая справка
    cli_cmd_func_t func;     // Указатель на функцию
} cli_command_t;

void cli_init(void);
void cli_rx_char(char c);    // Вызывать из прерывания UART RX
void cli_process(void);      // Вызывать в основном цикле while(1)

// Функцию отправки строки нужно реализовать под ваш МК
extern void uart_send_str(const char *str);

#endif
