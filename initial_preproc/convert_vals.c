#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>

int main() {
   // example input const char a[73] = "17:47:35.656	00-20-4B-3F-00-00-FA-BD-00-D0-84-BF-00-40-0E-3E-00-C0-29-3E";
   // Define variables
   char a[60];
   char c;
   
   // Print the timestamp
   for (int i=0; i<12; i++){
      c = getchar();
      printf("%c", c);
   }
   c = getchar();
   
   // Get the values
   for (int i=0; i<60; i++){
      c = getchar();
      a[i]=c;
   }

   // Convert the string to a byte array
   unsigned char b[20];
   char* ptr;
   for (int i=0; i<20; i++){
       b[i] = (unsigned char) strtol(&a[3*i], &ptr, 16);
   }
   
   // Convert byte array to float and write to csv stdout
   float* f;
   f = (float*) &b[0];
   for (int i=0; i<5; i++){
       printf(",%f",f[i]);
   }
   printf("\n");
   return 0;
}

