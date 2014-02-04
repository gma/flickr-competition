import unittest
import tally


class VoteTest(unittest.TestCase):

    def expected(self):
        return { '14': 1, '8': 2, '6': 3 }

    def test_points_returns_dict_of_scores(self):
        vote = tally.Vote("#6 - 3 pts\n#8 - 2 pts\n#14 - 1 pt")
        self.assertEqual(vote.points(), self.expected())

    def test_points_isnt_sensitive_to_whitespace(self):
        vote = tally.Vote("#6- 3 pts\n# 8 - 2pts\n #14 - 1 pt")
        self.assertEqual(vote.points(), self.expected())

    def test_points_suffix_isnt_required(self):
        vote = tally.Vote("#6 - 3\n#8 - 2 \n #14 - 1")
        self.assertEqual(vote.points(), self.expected())

    def test_points_works_with_variety_of_delimiters(self):
        vote = tally.Vote("#6 3 pts. #8: 2pts\n #14 = 1 pt")
        self.assertEqual(vote.points(), self.expected())

    def test_points_is_relaxed_about_prefix_and_suffix(self):
        vote = tally.Vote("No 6 - 3 pts\nNo. 8 - 2 points\n14# - 1 point")
        self.assertEqual(vote.points(), self.expected())

    def test_tally_adds_up_all_the_scores(self):
        votes = [
            tally.Vote("#6 - 3 pts\n#8 - 2 pts\n#14 - 1 pt"),
            tally.Vote("#5 - 3 pts\n#6 - 2 pts\n#8 - 1 pt")
        ]
        results = { '6': 5, '5': 3, '8': 3, '14': 1 }
        self.assertEqual(tally.Vote.tally(votes), results)


if __name__ == '__main__':
    unittest.main()
