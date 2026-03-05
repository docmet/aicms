"use client";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { Plus, Trash2 } from "lucide-react";

interface PricingPlan {
  name: string;
  price: string;
  period?: string;
  features: string[];
  cta_label?: string;
  cta_href?: string;
  highlighted?: boolean;
}

interface PricingContent {
  headline?: string;
  subheadline?: string;
  plans: PricingPlan[];
}

interface Props {
  content: PricingContent;
  onChange: (content: PricingContent) => void;
}

export function PricingEditor({ content, onChange }: Props) {
  const set = (patch: Partial<PricingContent>) => onChange({ ...content, ...patch });
  const plans = content.plans || [];

  const setPlan = (i: number, patch: Partial<PricingPlan>) => {
    set({ plans: plans.map((p, idx) => (idx === i ? { ...p, ...patch } : p)) });
  };
  const addPlan = () =>
    set({ plans: [...plans, { name: "", price: "", features: [], cta_label: "Get started" }] });
  const removePlan = (i: number) => set({ plans: plans.filter((_, idx) => idx !== i) });

  const setFeature = (planIdx: number, featIdx: number, value: string) => {
    const features = [...(plans[planIdx].features || [])];
    features[featIdx] = value;
    setPlan(planIdx, { features });
  };
  const addFeature = (planIdx: number) =>
    setPlan(planIdx, { features: [...(plans[planIdx].features || []), ""] });
  const removeFeature = (planIdx: number, featIdx: number) =>
    setPlan(planIdx, { features: plans[planIdx].features.filter((_, i) => i !== featIdx) });

  return (
    <div className="space-y-4">
      <div className="grid grid-cols-2 gap-4">
        <div className="space-y-1.5">
          <Label>Headline</Label>
          <Input value={content.headline || ""} onChange={(e) => set({ headline: e.target.value })} placeholder="Pricing" />
        </div>
        <div className="space-y-1.5">
          <Label>Subheadline</Label>
          <Input value={content.subheadline || ""} onChange={(e) => set({ subheadline: e.target.value })} placeholder="Simple, honest pricing" />
        </div>
      </div>

      <div>
        <div className="flex items-center justify-between mb-2">
          <Label>Plans ({plans.length})</Label>
          <Button type="button" size="sm" variant="outline" onClick={addPlan} disabled={plans.length >= 4}>
            <Plus size={14} className="mr-1" /> Add Plan
          </Button>
        </div>
        <div className="space-y-4">
          {plans.map((plan, i) => (
            <div key={i} className="p-4 border rounded-lg bg-muted/30 space-y-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Switch
                    checked={plan.highlighted || false}
                    onCheckedChange={(v) => setPlan(i, { highlighted: v })}
                  />
                  <span className="text-xs text-muted-foreground">Highlighted</span>
                </div>
                <Button type="button" variant="ghost" size="icon" className="text-muted-foreground hover:text-destructive" onClick={() => removePlan(i)}>
                  <Trash2 size={14} />
                </Button>
              </div>
              <div className="grid grid-cols-3 gap-2">
                <Input value={plan.name} onChange={(e) => setPlan(i, { name: e.target.value })} placeholder="Plan name *" className="text-sm" />
                <Input value={plan.price} onChange={(e) => setPlan(i, { price: e.target.value })} placeholder='Price e.g. "$29"' className="text-sm" />
                <Input value={plan.period || ""} onChange={(e) => setPlan(i, { period: e.target.value })} placeholder='Period e.g. "/month"' className="text-sm" />
              </div>
              <div className="grid grid-cols-2 gap-2">
                <Input value={plan.cta_label || ""} onChange={(e) => setPlan(i, { cta_label: e.target.value })} placeholder="Button label" className="text-sm" />
                <Input value={plan.cta_href || ""} onChange={(e) => setPlan(i, { cta_href: e.target.value })} placeholder="Button URL" className="text-sm" />
              </div>
              <div>
                <div className="flex items-center justify-between mb-1">
                  <Label className="text-xs">Features</Label>
                  <Button type="button" size="sm" variant="ghost" className="h-6 text-xs px-2" onClick={() => addFeature(i)}>
                    <Plus size={12} className="mr-1" /> Add
                  </Button>
                </div>
                <div className="space-y-1">
                  {(plan.features || []).map((feat, j) => (
                    <div key={j} className="flex gap-1">
                      <Input value={feat} onChange={(e) => setFeature(i, j, e.target.value)} placeholder="Feature" className="text-sm h-7" />
                      <Button type="button" variant="ghost" size="icon" className="h-7 w-7 text-muted-foreground hover:text-destructive" onClick={() => removeFeature(i, j)}>
                        <Trash2 size={12} />
                      </Button>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
