export interface CompanySummary {
  company_id: number;
  ticker: string;
  company_name: string;
  company_logo?: string | null;
  website?: string | null;
  face_value?: number | null;
  book_value?: number | null;
  roce_percentage?: number | null;
  roe_percentage?: number | null;
  latest_revenue?: number | null;
  latest_net_profit?: number | null;
  health_score?: number | null;
  health_label?: string | null;
}

export interface BalanceSheet {
  year: number;
  total_assets?: number | null;
  total_liabilities?: number | null;
}

export interface ProfitAndLoss {
  year: number;
  sales?: number | null;
  net_profit?: number | null;
  eps?: number | null;
}

export interface CashFlow {
  year: number;
  net_cash_flow?: number | null;
}

export interface Analysis {
  compounded_sales_growth?: number | null;
  compounded_profit_growth?: number | null;
  stock_price_cagr?: number | null;
  roe_percentage?: number | null;
}

export interface ProsCons {
  pros?: string | null;
  cons?: string | null;
}

export interface Document {
  year?: number | null;
  annual_report?: string | null;
}

export interface CompanyDetail {
  company_id: number;
  ticker: string;
  company_name: string;
  company_logo?: string | null;
  chart_link?: string | null;
  about_company?: string | null;
  website?: string | null;
  nse_profile?: string | null;
  bse_profile?: string | null;
  face_value?: number | null;
  book_value?: number | null;
  roce_percentage?: number | null;
  roe_percentage?: number | null;
  balance_sheets: BalanceSheet[];
  profit_and_losses: ProfitAndLoss[];
  cash_flows: CashFlow[];
  documents: Document[];
  analysis?: Analysis | null;
  pros_cons?: ProsCons | null;
}

export interface HealthScore {
  company_id: number;
  ticker: string;
  company_name: string;
  year: number;
  score: number;
  label: string;
}

export interface CompanyMetrics {
  company: string;
  company_name: string;
  metrics: ProfitAndLoss[];
}

export interface CompanyScores {
  company: string;
  scores: HealthScore[];
}

export interface ListResponse<T> {
  count: number;
  results: T[];
}
