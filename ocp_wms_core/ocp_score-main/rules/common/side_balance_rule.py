from domain.space_size import SpaceSize
from domain.space import Space
from domain.mounted_space_list import MountedSpaceList
from domain.space_list import SpaceList
from domain.base_rule import BaseRule
from domain.context import Context
from dataclasses import dataclass


@dataclass
class SpaceWithMountedSpaceDto:
    Space: object
    MountedSpace: object


class SideBalanceRule(BaseRule):
    def __init__(self):
        super().__init__(name='SideBalanceRule')

    def should_execute(self, context: Context) -> bool:
        # return False
        if not context.get_setting('SideBalanceRule', False):
            context.add_execution_log('Regra desativada, nao sera executada')
            return False
        if not getattr(context, 'mounted_spaces', None):
            context.add_execution_log('Nenhuma baia montada, a regra nao sera executada')
            return False
        return True

    def execute(self, context: Context) -> Context:
        context.add_execution_log('Iniciando execucao da regra')

        # Faithful port of C# SideBalanceRule flow
        percentage = self._get_percentage_weight_of_driver_side(context)
        context.add_execution_log(f'Inicio do balanceamento - Lado Motorista: {percentage:.2f}% - Lado Ajudante: {100.0 - percentage:.2f}%')
        # context.add_execution_log(self._get_pallet_weight_log_message(context))

        # Order mounted spaces by weight descending and run SideBalance
        try:
            mounted_spaces = MountedSpaceList(context.MountedSpaces).OrderByWeightDesc()
        except Exception as e:
            print(f"Error:: {e}")
            # fallback to simple sort if C#-style helper not present
            mounted_spaces = sorted(getattr(context, 'mounted_spaces', []) or [], key=lambda x: getattr(x, 'weight', 0), reverse=True)

        self._side_balance(context, mounted_spaces)

        ##teste  pode deletar depois
        percentage = self._get_percentage_weight_of_driver_side(context)
        context.add_execution_log(f'Inicio do balanceamento - Lado Motorista: {percentage:.2f}% - Lado Ajudante: {100.0 - percentage:.2f}%')
        ##teste 
        # Ensure driver side weight is greater if helper side heavier (C# behavior)
        self._ensure_driver_side_weight_is_greater(context)

        percentage = self._get_percentage_weight_of_driver_side(context)
        context.add_execution_log(f'Fim do balanceamento - Lado Motorista: {percentage:.2f}% - Lado Ajudante: {100.0 - percentage:.2f}%')
        # context.add_execution_log(self._get_pallet_weight_log_message(context))

        return context

    def _side_balance(self, context: Context, mounted_spaces):
        for mounted_space in mounted_spaces:
            is_driver_side = self._is_driver_side(context)
            target_space = self._get_first_space_not_balanced(context, mounted_space, is_driver_side)
            if not target_space:
                context.add_execution_log(f'Nenhuma baia encontrada para balancear os produtos da Baia:{getattr(mounted_space.Space if hasattr(mounted_space, "Space") else mounted_space, "side", "?")}/{getattr(mounted_space.Space if hasattr(mounted_space, "Space") else mounted_space, "number", "?")} - Peso:{getattr(mounted_space, "weight", 0):.2f}')
                continue

            target_mounted_space = context.get_mounted_space(target_space)

            if not target_mounted_space or self._get_mounted_space_occupation(target_mounted_space, mounted_space.space.size, context.get_setting('OccupationAdjustmentToPreventExcessHeight', False)) <= mounted_space.space.size:
                self._switch_spaces_and_set_balanced(context, mounted_space, target_space)
            else:
                self._search_new_space_to_switch(context, mounted_space, target_mounted_space, target_space, is_driver_side)

    def _is_driver_side(self, context: Context) -> bool:
        try:
            driver = sum(x.weight for x in MountedSpaceList(context.GetMountedSpacesBalanced()).DriverSide())
            helper = sum(x.weight for x in MountedSpaceList(context.GetMountedSpacesBalanced()).HelperSide())
            return driver <= helper
        except Exception as e:
            print("Error determining driver side:", e)
            # fallback: compute using simple sums
            driver = sum(getattr(ms, 'weight', 0) for ms in getattr(context, 'mounted_spaces', []) or [] if getattr(getattr(ms, 'space', None), 'side', '').strip().lower().startswith('d'))
            helper = sum(getattr(ms, 'weight', 0) for ms in getattr(context, 'mounted_spaces', []) or [] if not getattr(getattr(ms, 'space', None), 'side', '').strip().lower().startswith('d'))
            return driver <= helper

    def _get_first_space_not_balanced(self, context, mounted_space, is_driver_side):
        # 1. pegar todos os spaces
        spaces = context.get_all_spaces()

        # 2. NotBalanced() filtrado (assumindo que existe esse método)
        spaces = SpaceList(context.GetAllSpaces()).NotBalanced().spaces

        # 3. aplicar o filtro do tamanho
        spaces = [
            s for s in spaces
            if float(s.size) >= self._get_mounted_space_occupation(
                mounted_space,
                s.size,
                context.get_setting('OccupationAdjustmentToPreventExcessHeight', False)
            )
        ]
        # 4. ordenar por IsDriverSide DESC, Number ASC
        spaces_sorted = sorted(
            spaces,
            key=lambda s: (
                -(s.is_driver_side() == is_driver_side),  # DESC
                s.number                                 # ASC
            )
        )

        # 5. retornar o primeiro ou None
        return spaces_sorted[0] if spaces_sorted else None


    # def _get_first_space_not_balanced(self, context: Context, mounted_space, is_driver_side):
    #     try:
    #         spaces = SpaceList(context.GetAllSpaces()).NotBalanced().matching(lambda x: x.Size >= self._get_mounted_space_occupation(mounted_space, x.Size, context.get_setting('OccupationAdjustmentToPreventExcessHeight', False)))
    #         ordered = spaces.OrderByDescending(lambda x: x.IsDriverSide() == is_driver_side).ThenBy(lambda x: x.Number)
    #         return ordered.FirstOrDefault()
    #     except Exception as e:
    #         print(f"Error:: {e}")
    #         # fallback: simple scan 
    #         candidates = [s for s in getattr(context, 'spaces', []) or [] if getattr(s, 'size', 0) >= self._get_mounted_space_occupation(mounted_space, getattr(s, 'size', 0), context.get_setting('OccupationAdjustmentToPreventExcessHeight', False)) and not getattr(s, 'balanced', False)]
    #         candidates.sort(key=lambda x: (1 if getattr(x, 'side', '').strip().lower().startswith('d') == is_driver_side else 0, getattr(x, 'number', 0)), reverse=True)
    #         return candidates[0] if candidates else None

    def _switch_spaces_and_set_balanced(self, context: Context, mounted_space, target_space):
        # find mounted space instances
        target_mounted_space = context.get_mounted_space(target_space)

        is_different = mounted_space.Space.Number != target_space.Number or (mounted_space.Space.Side != target_space.Side)
        if is_different:
            context.add_execution_log(f'Movendo os produtos da Baia:{mounted_space.Space.Side}/{mounted_space.Space.Number} para a Baia:{target_space.Side}/{target_space.Number}')
            try:
                # pass the actual MountedSpace instances so domain operations mutates context state
                context.domain_operations.switch_spaces(context, mounted_space, target_mounted_space, target_space)
                if target_mounted_space is None:
                    target_mounted_space = context.get_mounted_space(target_space)
            except Exception:
                # fallback: try passing mounted spaces directly if signature differs
                try:
                    context.domain_operations.switch_spaces(mounted_space, target_mounted_space)
                except Exception:
                    pass
        self._recalculate_mounted_space_occupation(context, target_mounted_space)
        self._adjust_closed_pallet(context, target_mounted_space)

        try:
            target_space.SetBalanced()
        except Exception as e:
            print(f"Error:: {e}")
            try:
                target_space.set_balanced()
            except Exception as e:
                print(f"Error:: {e}")
                pass

    def _switch_spaces(self, context: Context, space, target_space):
        current_ms = context.get_mounted_space(space)
        target_ms = context.get_mounted_space(target_space)
        context.add_execution_log(f'Movendo os produtos da Baia:{space.Side}/{space.Number} para a Baia:{target_space.Side}/{target_space.Number}')
        try:
            context.domain_operations.switch_spaces(context, current_ms, target_ms, target_space)
        except Exception:
            try:
                context.domain_operations.switch_spaces(current_ms, target_ms)
            except Exception:
                pass

    def _ensure_driver_side_weight_is_greater(self, context: Context):
        # driver = sum(getattr(ms, 'weight', 0) for ms in getattr(context, 'mounted_spaces', []) or [] if getattr(getattr(ms, 'space', None), 'side', '').strip().lower().startswith('d'))
        # helper = sum(getattr(ms, 'weight', 0) for ms in getattr(context, 'mounted_spaces', []) or [] if not getattr(getattr(ms, 'space', None), 'side', '').strip().lower().startswith('d'))

        driver = sum(x.weight for x in MountedSpaceList(context.mounted_spaces).DriverSide())
        helper = sum(x.weight for x in MountedSpaceList(context.mounted_spaces).HelperSide())
        
        if helper > driver:
            context.add_execution_log('Lado do Ajudante com peso maior que o Lado do Motorista, invertendo as baias')
            helper_spaces = context.domain_operations.ordered_by(SpaceList(context.GetAllSpaces()).HelperSide(), [("Number", "asc")])
            # helper_spaces.sort(key=lambda x: getattr(x, 'number', 0))
            for helper_space in helper_spaces:
                current = SpaceWithMountedSpaceDto(helper_space, context.get_mounted_space(helper_space))
                # target = next((x for x in getattr(context, 'spaces', []) or [] if getattr(x, 'side', '').strip().lower().startswith('d') and getattr(x, 'number', None) == getattr(helper_space, 'number', None)), None)
                target = SpaceList(context.GetAllSpaces()).DriverSide().getSpaceByNumber(helper_space.number)
                if not target:
                    continue
                target_ms = context.get_mounted_space(target)
                current_ms = context.get_mounted_space(helper_space)
                try:
                    context.domain_operations.switch_spaces(context, current_ms, target_ms, target)
                except Exception as e:
                    print(f"Error:: {e}")
                    try:
                        context.domain_operations.switch_spaces(current_ms, target_ms)
                    except Exception as e:
                        print(f"Error:: {e}")
                        pass

    def _search_new_space_to_switch(self, context: Context, mounted_space, target_mounted_space, target_space, is_driver_side):
        if self._try_switch_target_mounted_space_to_empty_space(context, mounted_space, target_mounted_space, target_space, is_driver_side):
            return
        if self._try_switch_target_space_to_another_mounted_space(context, mounted_space, target_mounted_space, target_space, is_driver_side):
            return
        self._find_new_space_with_same_size_spaces(context, mounted_space, is_driver_side)

    def _try_switch_target_mounted_space_to_empty_space(self, context: Context, mounted_space, target_mounted_space, target_space, is_driver_side):
        available = [s for s in getattr(context, 'spaces', []) or [] if getattr(s, 'size', 0) >= self._get_mounted_space_occupation(target_mounted_space, getattr(s, 'size', 0), context.get_setting('OccupationAdjustmentToPreventExcessHeight', False))]
        if available:
            space_to_switch = self._find_best_space_to_switch(available, is_driver_side)
            self._switch_spaces(context, target_space, space_to_switch)
            self._switch_spaces_and_set_balanced(context, mounted_space, target_space)
            return True
        return False

    def _try_switch_target_space_to_another_mounted_space(self, context: Context, mounted_space, target_mounted_space, target_space, is_driver_side):
        candidates = []
        for x in getattr(context, 'mounted_spaces', []) or []:
            if x.Space != mounted_space.Space and x.Space != target_space:
                if self._get_mounted_space_occupation(x, mounted_space.space.size, context.get_setting('OccupationAdjustmentToPreventExcessHeight', False)) <= mounted_space.space.size and getattr(x.Space, 'size', 0) >= self._get_mounted_space_occupation(target_mounted_space, getattr(x.Space, 'size', 0), context.get_setting('OccupationAdjustmentToPreventExcessHeight', False)):
                    candidates.append(x.Space)

        candidates = [s for s in candidates if not getattr(s, 'balanced', False)]
        if candidates:
            space_to_switch = self._find_best_space_to_switch(candidates, is_driver_side)
            self._switch_spaces(context, target_space, space_to_switch)
            self._switch_spaces_and_set_balanced(context, mounted_space, target_space)
            return True
        return False

    def _find_new_space_with_same_size_spaces(self, context: Context, mounted_space, is_driver_side):
        same_size = [s for s in getattr(context, 'spaces', []) or [] if getattr(s, 'size', None) == mounted_space.space.size and not getattr(s, 'balanced', False)]
        new_target = self._find_best_space_to_switch(same_size, is_driver_side)
        if new_target:
            self._switch_spaces_and_set_balanced(context, mounted_space, new_target)

    def _find_best_space_to_switch(self, spaces, is_driver_side):
        # Order by driver-side preference then by number
        try:
            ordered = sorted(spaces, key=lambda sp: (not getattr(sp, 'is_driver_side', lambda: False)() if callable(getattr(sp, 'is_driver_side', None)) else 0, getattr(sp, 'number', 0)), reverse=True)
            return ordered[0] if ordered else None
        except Exception as e:
            print(f"Error:: {e}")
            return spaces[0] if spaces else None

    def _get_mounted_space_occupation(self, mounted_space, size, calculate_additional_occupation):
        try:
            if mounted_space.space.size == size:
                return mounted_space.Occupation

            # emulate C#: use factor converter
            from ...domain.factor_converter import FactorConverter
            fc = FactorConverter()
            mounted_products = mounted_space.GetProducts()
            total = 0
            for mp in mounted_products:
                occ = fc.occupation(mp, size, getattr(mp, 'item', None), calculate_additional_occupation)
                total += float(occ)
            return total
        except Exception as e:
            print(f"Error:: {e}")
            return getattr(mounted_space, 'occupation', 0)

    def _get_percentage_weight_of_driver_side(self, context: Context) -> float:
        """
        Faithful port of C# GetPercentageWeightOfDriverSide:
        driverWeight * 100 / totalWeight
        """
        # call the context API directly (faithful to C# style)
        total_weight = sum(ms.weight for ms in context.mounted_spaces)
        driver_weight = sum(ms.weight for ms in MountedSpaceList(context.mounted_spaces).DriverSide())
        return float((driver_weight * 100 / total_weight) if total_weight != 0 else 0.0)

    def _recalculate_mounted_space_occupation(self, context: Context, mounted_space):
        try:
            old = mounted_space.occupation
            mounted_space.SetOccupation(0)
            for mp in mounted_space.get_products():
                try:
                    mp.Item.SetAdditionalOccupation(0)
                except Exception as e:
                    print("Error setting AdditionalOccupation:", e)
                    pass
                occ = self._get_product_total_occupation(mounted_space, mp, context.get_setting('OccupationAdjustmentToPreventExcessHeight', False))
                mountedProductOccupation = occ - mp.Item.AdditionalOccupation
                mp.SetOccupation(mountedProductOccupation)
                mounted_space.IncreaseOccupation(occ)
            context.add_execution_log(f'Recalculado ocupação da Baia:{getattr(mounted_space.space, "Side", "?")}/{getattr(mounted_space.space, "Number", "?")} - Antes:{old:.2f} - Depois:{getattr(mounted_space, "Occupation", 0):.2f}')
        except Exception as e:
            print("Error recalculating mounted space occupation:", e)
            pass

    def _get_product_total_occupation(self, mounted_space, mounted_product, calculate_additional_occupation):
        try:
            if mounted_space.GetFirstPallet().Bulk:
                return float(mounted_space.space.size)
            # get factor from product
            # factor = mounted_product.Product.Factors.FirstOrDefault(lambda f: f.Size == mounted_space.space.size)
            # factor = next((f for f in mounted_product.Product.factors if f.size == mounted_space.space.size), None)
            factor = mounted_product.Product.get_factor(mounted_space.space.size) 
            from ...domain.factor_converter import FactorConverter
            fc = FactorConverter()
            return fc.occupation(getattr(mounted_product, 'Amount', getattr(mounted_product, 'amount', 0)), factor, mounted_product.Product.PalletSetting, mounted_product.Item, calculate_additional_occupation)
        except Exception as e:
            print(f"Error:: {e}")
            return 0

    def _adjust_closed_pallet(self, context: Context, mounted_space):
        try:
            old = mounted_space.GetFirstPallet().Bulk
            if mounted_space.GetFirstPallet().Bulk and mounted_space.space.size < SpaceSize.Size42:
                mounted_space.GetFirstPallet().SetBulk(context.get_setting('BulkAllPallets', False))
            context.add_execution_log(f'Recalculando palete fechado da Baia:{getattr(mounted_space.Space, "Side", "?")}/{getattr(mounted_space.Space, "Number", "?")} - Antes: {old} - Depois: {mounted_space.GetFirstPallet().Bulk}')
        except Exception as e:
            print(f"Error:: {e}")
            pass

    def _get_pallet_weight_log_message(self, context: Context) -> str:
        parts = []
        for ms in sorted(getattr(context, 'mounted_spaces', []) or [], key=lambda x: getattr(x.Space if hasattr(x, 'Space') else x, 'Number', 0)):
            side = getattr(ms.Space if hasattr(ms, 'Space') else ms, 'Side', getattr(ms, 'space', {}).get('side', '?'))
            number = getattr(ms.Space if hasattr(ms, 'Space') else ms, 'Number', getattr(ms, 'space', {}).get('number', '?'))
            weight = getattr(ms, 'Weight', getattr(ms, 'weight', 0)) or 0
            parts.append(f"{side}/{number} weight: {weight:.2f}")
        return '; '.join(parts)
