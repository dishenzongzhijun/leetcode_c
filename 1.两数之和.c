/*
 * @Author       : liuben
 * @Date         : 2021-12-06 00:10:31
 * @LastEditors  : liuben
 * @LastEditTime : 2022-04-23 22:31:01
 * @Description  : 
 * @FilePath     : /leetcode_c/1.两数之和.c
 */

#include "god.h"

/*
 * @lc app=leetcode.cn id=1 lang=c
 *
 * [1] 两数之和
 */

// @lc code=start


/**
 * Note: The returned array must be malloced, assume caller calls free().
 */
int* twoSum(int* nums, int numsSize, int target, int* returnSize){
    int *res = (int *)malloc(sizeof(int) * 2);
    *returnSize = 2;
    for (int i = 0; i < numsSize -1; i++) {
        for (int j = i + 1; j < numsSize; j++) {
            if (nums[i] + nums[j] == target) {
                res[0] = i;
                res[1] = j;
                break;
            }
        }
    }
    return res;
}
// @lc code=end

