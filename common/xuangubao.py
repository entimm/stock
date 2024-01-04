from datetime import datetime
from typing import Union, Any, Dict


def format_timestamp(value: Union[str, int], formate: str) -> str:
    return '-' if value == '' else datetime.fromtimestamp(int(value)).strftime(formate)


def format_flow_capital(value: Union[str, float]) -> str:
    return '-' if value == '' else round(float(value) / 1e8, 2)


def row2info(row: Dict[str, Any]) -> Dict[str, Any]:
    stock_chi_name = row['stock_chi_name']
    symbol = row['symbol'][:-3]
    m_days_n_boards_days = row['m_days_n_boards_days']
    m_days_n_boards_boards = row['m_days_n_boards_boards']

    info = {
        'name': stock_chi_name,
        'symbol': symbol,
        'm_days_n_boards_boards': m_days_n_boards_boards,
        'limited_freq': f"{m_days_n_boards_days}天{m_days_n_boards_boards}板" if m_days_n_boards_boards else '首板',
        'turnover_ratio': f"{round(row['turnover_ratio'] * 100, 2)}",
        'break_times': row.get('break_limit_up_times', '-'),
        'first_limit_up': format_timestamp(row.get('first_limit_up', ''), '%H:%M:%S'),
        'last_limit_up': format_timestamp(row.get('last_limit_up', ''), '%H:%M:%S'),
        'listed_date': format_timestamp(row.get('listed_date', ''), '%Y-%m-%d'),
        'flow_capital': format_flow_capital(row.get('non_restricted_capital', '')),
        'buy_lock_volume_ratio': round(row.get('buy_lock_volume_ratio', -1) * 100, 2),
        'reason': f"{row.get('surge_reason.stock_reason', '-')}",
    }

    return info
