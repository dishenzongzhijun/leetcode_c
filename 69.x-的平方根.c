/*
 * @Author       : liuben
 * @Date         : 2022-04-22 20:11:52
 * @LastEditors  : liuben
 * @LastEditTime : 2022-04-24 01:21:31
 * @Description  : 
 * @FilePath     : /leetcode_c/69.x-的平方根.c
 */

#include "god.h"

/*
 * @lc app=leetcode.cn id=69 lang=c
 *
 * [69] x 的平方根
 */

// @lc code=start

int mySqrt(int x)
{
    // O(n)
    int res = 0;
    for (int i = 0; i < x; i++) {
        if (i * i > x) {
            res = i - 1;
        }
    }

    return res;

    // O(log n)
    int left = 0;
    int right = x;

    while (left < right)
    {
        int mid = left + (right - left) / 2;
        int tmp = mid * mid;
        if (tmp == x) {
            right = mid;
        } else if (tmp < x) {
            left = mid + 1;
        } else if (tmp > x) {
            right = mid;
        }
    }
    return left;
}
// @lc code=end
