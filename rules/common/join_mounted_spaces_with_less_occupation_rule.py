from ...domain.mounted_space_list import MountedSpaceList
from ...domain.base_rule import BaseRule


class JoinMountedSpacesWithLessOccupationRule(BaseRule):
    """Faithful port of the C# JoinMountedSpacesWithLessOccupationRule.

    This implementation deliberately calls methods/attributes directly to mirror
    the C# control flow. It expects a factor_converter to be provided by the
    caller that exposes an `Occupation` method used to compute occupation sums.
    """
    def __init__(self, factor_converter):
        super().__init__(name='JoinMountedSpacesWithLessOccupationRule')
        self._factor_converter = factor_converter

    def should_execute(self, context, item_predicate=None, mounted_space_predicate=None):
        # Mirror C# ShouldExecute: check configured threshold and existence of candidate
        if context.get_setting('OccupationToJoinMountedSpaces') < 1:
            context.add_execution_log("Ocupacao minima para juntar espaços montados nao foi informada. Nas configuraçoes de calculo -> JuntarPalletsComMenorOcupacao <= 0. Executando proxima regra.")
            return False

        if self._get_mounted_space_with_less_occupation(context) is None:
            context.add_execution_log("Nenhum espaço montado com ocupação menor que o limite configurado foi encontrado. Executando proxima regra.")
            return False

        return True

    def execute(self, context):
        mounted_space_with_less_occupation = self._get_mounted_space_with_less_occupation(context)

        while mounted_space_with_less_occupation is not None:
            # Get candidate to join (C#: GetMountedSpaces(context).WhereIsNot(...).OrderByOccupiedPercentage().FirstOrDefault())
            mounted_space_to_join = self._get_mounted_spaces(context).WhereIsNot(mounted_space_with_less_occupation).OrderByOccupiedPercentage().FirstOrDefault()

            if mounted_space_to_join is None:
                context.add_execution_log(f"Não encontrado um pallet valido para unir com o pallet {mounted_space_with_less_occupation.Space}")
                break

            # order by space number as in C# and pick target/source ordering
            mounted_spaces_to_join = sorted([mounted_space_with_less_occupation, mounted_space_to_join], key=lambda x: x.Space.Number)

            if not self._move_mounted_space_products(context, mounted_spaces_to_join[0], mounted_spaces_to_join[1]):
                break

            mounted_space_with_less_occupation = self._get_mounted_space_with_less_occupation(context)

        return context

    def _get_mounted_spaces(self, context):
        # direct port of C# helper: context.MountedSpaces.WithProducts().HasSpaceAndNotBlocked()
        return MountedSpaceList(context.MountedSpaces).WithProducts().HasSpaceAndNotBlocked()

    def _get_mounted_space_with_less_occupation(self, context):
        # C#: GetMountedSpaces(context).WithOccupationLessThan(context.Settings.OccupationToJoinMountedSpaces).OrderByOccupiedPercentage().FirstOrDefault();
        mounted_space = self._get_mounted_spaces(context).WithOccupationLessThan(context.get_setting('OccupationToJoinMountedSpaces')).OrderByOccupiedPercentage().FirstOrDefault()

        if mounted_space is None:
            context.add_execution_log(f"Não há palete com ocupação inferior a {context.get_setting('OccupationToJoinMountedSpaces')}%")

        return mounted_space

    def _move_mounted_space_products(self, context, target, source):
        # gather products from containers (equivalent to C# SelectMany + Concat)
        source_products = [p for c in source.containers for p in c.products]
        target_products = [p for c in target.containers for p in c.products]
        all_products = target_products + source_products

        # Sum occupation using factor converter
        def prod_occupation(x):
            return float(self._factor_converter.occupation(x.amount, x.Product.GetFactor(target.Space.Size), \
                                                           x.Product.PalletSetting, x.item, \
                                                           context.get_setting('OccupationAdjustmentToPreventExcessHeight')))


        total_occupation = sum(prod_occupation(x) for x in all_products)

        if target.space.Size < total_occupation:
            context.add_execution_log(f"Os itens da baia ({source.space}) não cabem na baia ({target.space}). A baia de destino ficaria com ocupação total: ({total_occupation}). Finalizando Execução da regra")
            return False

        # Move products and log
        products_to_move = ", ".join([f"Cod:{p.product.Code} Qtd:{p.amount}" for p in source_products])
        context.add_execution_log(f"Movendo os produts ({products_to_move}) de ({source.space}) para ({target.space}).")
        # perform switch
        context.switch_products(target, source, total_occupation)
        context.add_execution_log(f"Os produtos foram movidos de ({source.space}) para ({target.space}), nova ocupacao de {target.Occupation}")
        return True
