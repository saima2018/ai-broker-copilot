from commons.intention_script_loader import intention_script_df


def filter_conditions(intention_script_df=intention_script_df):

    filtered_intention_script_df = intention_script_df.drop_duplicates(subset='intention', keep='first')

    return filtered_intention_script_df