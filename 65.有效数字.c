/*
 * @Author       : liuben
 * @Date         : 2021-12-06 00:10:31
 * @LastEditors  : liuben
 * @LastEditTime : 2022-04-23 22:24:33
 * @Description  :
 * @FilePath     : /leetcode_c/65.有效数字.c
 */

#include "god.h"

/*
 * @lc app=leetcode.cn id=65 lang=c
 *
 * [65] 有效数字
 */

// @lc code=start

bool isNumber(int num)
{
    return true;
}

// @lc code=end

int main()
{
    int num = 9;
    bool res = false;
    printf("ok:%d\n", num);
    num += 3;
    printf("ok:%d\n", num);
    res = isNumber(num);
    return 0;
}