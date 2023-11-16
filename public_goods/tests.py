from otree.api import Currency as cu, currency_range
from public_goods import pages
from ._builtin import Bot
from .models import Constants, Player

class PlayerBot(Bot):

    def play_round(self):
        # Assuming a strategy for contributions and punishments to test
        contribution = cu(20)
        punishments = {f'punish_p{p}': 1 for p in range(1, Constants.PLAYERS_PER_GROUP + 1) if p != self.player.id_in_group}

        # Test for contributions
        yield pages.Contribute, {'contribution': contribution}
        assert self.player.contribution == contribution, 'Contribution does not match expected value.'

        # Test for punishment allocations
        yield pages.Punish, punishments
        for p_num, punishment in punishments.items():
            other_player = self.player.in_round(self.round_number).get_others_in_group()[int(p_num[-1]) - 1]
            assert getattr(other_player, p_num) == punishment, f'Punishment allocation for {p_num} does not match expected value.'

        # Test for final payoffs calculation
        yield pages.WaitPage2
        total_contribution = sum([p.contribution for p in self.group.get_players()])
        individual_share = total_contribution * Constants.MULTIPLIER / Constants.PLAYERS_PER_GROUP
        payoff_before_punishment = Constants.ENDOWMENT - self.player.contribution + individual_share
        punishments_received = sum(getattr(p, f'punish_p{self.player.id_in_group}') for p in self.player.get_others_in_group())
        cost_of_punishing = sum(Constants.PUNISHMENT_SCHEDULE[getattr(self.player, f'punish_p{p.id_in_group}')] for p in self.player.get_others_in_group())
        expected_payoff = payoff_before_punishment - punishments_received - cost_of_punishing

        assert self.player.payoff == expected_payoff, 'Payoff calculation does not match expected value.'

        # Proceed to results
        yield pages.Results
