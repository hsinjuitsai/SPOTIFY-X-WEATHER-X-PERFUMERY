export default defineComponent({
  async run({ steps, $ }) {
    const raw = steps.generate_content_from_text.$return_value.candidates[0].content.parts[0].text;
    const clean = raw.replace(/```json|```/g, "").trim();
    const copy = JSON.parse(clean);
    const name = String(copy.AI_Scent || "");
    const reasoning = String(copy.AI_Reasoning || "");
    if (!/^[\u3400-\u9fff]{4}$/u.test(name)) throw new Error("AI_Scent must contain exactly four Chinese characters");
    if ([...reasoning].length > 20) throw new Error("AI_Reasoning must be 20 characters or fewer");
    const decision = steps.logic_processor.$return_value.decision;
    const metrics = steps.logic_processor.$return_value.metrics;
    const slots = steps.session_manager.$return_value.slots;
    return {
      AI_Scent: name,
      AI_Reasoning: reasoning,
      current_song: metrics.current_song,
      fan_speed: decision.fan_speed,
      slot_a_name: slots.slot_a, slot_a_val: decision.ratios.slot_a || 0,
      slot_b_name: slots.slot_b, slot_b_val: decision.ratios.slot_b || 0,
      slot_c_name: slots.slot_c, slot_c_val: decision.ratios.slot_c || 0,
      slot_d_name: slots.slot_d, slot_d_val: decision.ratios.slot_d || 0,
    };
  },
});

