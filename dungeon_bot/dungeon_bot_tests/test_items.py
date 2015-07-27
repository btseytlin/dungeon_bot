"""Test random dice generation"""
from util import *
#get_dice_in_range(["1d1", "6d6"], 1)
def test_random_dice():
	left = 1
	right = 100
	coolity = 1
	randoms = []
	for x in range(10000):
		randoms.append(random_in_range_for_coolity(left, right, coolity))

	top = list(filter(lambda x: x > 0.8*right, randoms))
	bottom = list(filter(lambda x: x < 0.2*right, randoms))
	print("Avg rangom %f"%(sum(randoms)/len(randoms)))
	print("%d top value occurencies"%(len(top)))
	print("%d bottom value occurencies"%(len(bottom)))
	print("%d middle value occurencies"%(abs(len(randoms)-len(top)-len(bottom))))

	coolity = 0
	dices = []
	for x in range(10):
		dices.append(get_dice_in_range(["1d1","6d6"], coolity))
	print(", ".join(dices))

def run_tests():
	test_random_dice()