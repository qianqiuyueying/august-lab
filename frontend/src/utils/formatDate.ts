import { formatDistanceToNow, parseISO } from 'date-fns';
import { zhCN } from 'date-fns/locale';

export function formatDate(date: string | null | undefined): string {
  if (!date) return '';
  try {
    return formatDistanceToNow(parseISO(date), { addSuffix: true, locale: zhCN });
  } catch {
    return date;
  }
}
