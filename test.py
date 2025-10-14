def is_odd(n: int) -> bool:
	"""Return True if integer n is odd.

	Args:
		n: an integer value.

	Returns:
		True if n is odd, False otherwise.

	Raises:
		TypeError: if n is not an int. This project prefers explicit type checks
		for small utility functions to avoid surprising behaviour with floats.
	"""
	if not isinstance(n, int):
		raise TypeError("is_odd expects an int")
	# Use bitwise and for a fast check that also works for negative ints
	return (n & 1) != 0


if __name__ == '__main__':
	# quick smoke tests / examples
	cases = [(-3, True), (-2, False), (0, False), (1, True), (2, False), (999999, True)]
	for val, expected in cases:
		result = is_odd(val)
		print(f'is_odd({val}) -> {result} (expected {expected})')
		assert result == expected

	# show TypeError for non-int input
	try:
		is_odd(2.5)
	except TypeError as e:
		print('Type check test passed (float rejected):', e)
	else:
		raise SystemExit('Type check failed: float accepted')

	print('All tests passed')

