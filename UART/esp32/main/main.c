#include <stdio.h>
// FreeRTOS includes
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

// UART driver
#include "driver/uart.h"

// Error library
#include "esp_err.h"

#include "string.h"

// read a line from the UART controller
char* read_line(uart_port_t uart_controller) {
	static char line[1024];
	char *ptr = line;
	while(1) {
	
		int num_read = uart_read_bytes(uart_controller, (unsigned char *)ptr, 1, portMAX_DELAY);
		if(num_read == 1) {
			// new line found, terminate the string and return 
            //printf("received char: %c", *ptr);
			if(*ptr == '\n') {
				ptr++;
				*ptr = '\0';
				return line;
			}
			
			// else move to the next char
			ptr++;
		}
	}
}

// Main application
void app_main() {

	printf("UART echo\r\n\r\n");
	
	// configure the UART1 controller
	uart_config_t uart_config = {
        .baud_rate = 9600,
        .data_bits = UART_DATA_8_BITS,
        .parity    = UART_PARITY_DISABLE,
        .stop_bits = UART_STOP_BITS_1,
        .flow_ctrl = UART_HW_FLOWCTRL_DISABLE
    };
    uart_param_config(UART_NUM_1, &uart_config);
    uart_set_pin(UART_NUM_1, 22, 23, UART_PIN_NO_CHANGE, UART_PIN_NO_CHANGE); //TX , RX
    uart_driver_install(UART_NUM_1, 1024, 0, 0, NULL, 0);
    uint8_t *data = (uint8_t *) malloc(1024);
    char strout[5];
    //uint8_t *dataout = (uint8_t *) malloc(1024);
    for (int k=0; k<5; k++){
        for (int i=0; i<2;i++){
            sprintf(strout, "%3d%3d ", k, i);
            uart_write_bytes(UART_NUM_1, strout , 7);
            uart_write_bytes(UART_NUM_1, "Ready! Ciao a tutti!!!!!!!!!!\r\n", sizeof("Ready! Ciao a tutti!!!!!!!!!!\r\n"));
            
            for (int c = 1; c <= 321; c++)
                for (int d = 1; d <= 321; d++)
                    {}
            // Read data from the UART1
            int len = uart_read_bytes(UART_NUM_1, data, 120, 220 / portTICK_RATE_MS);
            
            // Write data back to the UART
            if(len > 0) {
                data[len] = '\0';
                printf("%s", data);
                //fflush(stdout);
            }
        }
    }
	/* configure the UART2 controller
    uart_param_config(UART_NUM_2, &uart_config);
    uart_set_pin(UART_NUM_2, 22, 23, UART_PIN_NO_CHANGE, UART_PIN_NO_CHANGE);
    uart_driver_install(UART_NUM_2, 1024, 0, 0, NULL, 0);
	
	
	uart_write_bytes(UART_NUM_2, "Ready!\r\n", 8);
	uint8_t *data2 = (uint8_t *) malloc(1024);
    
    int stream[500];
    for (int i=0;i<500;i++){
        stream[i]=0;
    } 
    */
    printf("Entering while loop!!!!!\r\n");
    while (1) {
        //get data from stdin
        //int len = fgets(data,1024,stdin);

		// Read data from the UART1
        char *line = read_line(UART_NUM_1);
    
		// Write data back to the UART
		printf("%s", line);
        uart_write_bytes(UART_NUM_1,line, strlen(line));
		fflush(stdout);
		}
}