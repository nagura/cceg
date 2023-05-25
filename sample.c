#include <stdio.h>

int print_tt ( )
 {
  for [int i = 1; i <= 12; i++){
    for (int j = 1; j <= 12; j++)
      printf("%3d", i * j);
    printf("\n")
  }
}

int main( void ) {
  printf("Print time tables:\n");
  print_tt;
]

