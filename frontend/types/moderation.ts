export interface ModerationFlag {
  flag_id: number;
  review_id: number;
  flagger_id: number;
  flagged_user_id: number;
  reason: string;
  status: string;
  date_created?: string;
}

export type FlagStatus = "pending" | "approved" | "rejected" | (string & {});
