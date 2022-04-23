/*
 * @Author       : liuben
 * @Date         : 2021-12-06 00:38:40
 * @LastEditors  : liuben
 * @LastEditTime : 2022-04-24 01:00:09
 * @Description  :
 * @FilePath     : /leetcode_c/35.搜索插入位置.c
 */

#include "god.h"

/*
 * @lc app=leetcode.cn id=35 lang=c
 *
 * [35] 搜索插入位置
 */

// @lc code=start

int searchInsert(int *nums, int numsSize, int target)
{
    // O(n)
    int index = 0;
    for (int i = 0; i < numsSize; i++)
    {
        if (target <= nums[i])
        {
            index = i;
        }
    }

    return index;

    // O(log n)
    int left = 0;
    int right = numsSize;

    while (left < right)
    {
        int mid = left + (right - left) / 2;
        if (nums[mid] == target) {
            right = mid;
        } else if (nums[mid] < target) {
            left = mid + 1;
        } else if (nums[mid] > target) {
            right = mid;
        }
    }
    return left;
}
// @lc code=end
