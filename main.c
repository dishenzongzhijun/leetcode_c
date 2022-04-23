/*
 * @Author       : liuben
 * @Date         : 2022-04-23 22:35:28
 * @LastEditors  : liuben
<<<<<<< HEAD
 * @LastEditTime : 2022-04-24 00:10:35
=======
 * @LastEditTime : 2022-04-23 23:59:22
>>>>>>> c371e807a2cd841f0ecb5a48f3a8a9dbd68e78db
 * @Description  : general main function
 * @FilePath     : /leetcode_c/main.c
 */

#include "god.h"

int main()
{
    int a_size = 100;
    int *nums_a = (int *)malloc(sizeof(int) * a_size);
    // memset是对连续的n个字节进行赋值。但是int类型占4个字节。
    memset(nums_a, 0, sizeof(int) * a_size);
    for (int i = 0; i < a_size; i++)
    {
        nums_a[i] = 1;
        // printf("val:0x%x ", nums_a[i]);
    }

    int b_size = 100;
    int *nums_b = (int *)malloc(sizeof(int) * a_size);
    memset(nums_b, 0, sizeof(nums_b));

    free(nums_a);
    free(nums_b);

    printf("amend");

    return 0;
}
