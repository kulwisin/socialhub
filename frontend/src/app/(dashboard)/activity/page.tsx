import { Header } from "@/components/layout/Header";
import { Card, CardContent } from "@/components/ui/card";
import { ActivityFeed } from "@/features/activity/ActivityFeed";

export default function ActivityPage() {
  return (
    <>
      <Header
        title="Activity Log"
        description="A full audit trail of everything that happens in SocialHub."
      />
      <div className="flex-1 p-8">
        <Card>
          <CardContent className="p-6">
            <ActivityFeed limit={100} />
          </CardContent>
        </Card>
      </div>
    </>
  );
}
