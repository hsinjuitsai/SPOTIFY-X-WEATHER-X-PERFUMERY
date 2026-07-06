export default defineComponent({
  props: { scent_db: { type: "data_store" } },
  async run({ steps, $ }) {
    const state = steps.session_manager.$return_value;
    const metrics = steps.logic_processor.$return_value.metrics;
    const key = `session:${state.session_id}`;
    const session = await this.scent_db.get(key);
    if (!session) return { success: false, reason: "session_not_found" };
    session.last_song = metrics.current_song;
    session.last_energy = metrics.energy;
    session.last_valence = metrics.valence;
    session.updated_at = new Date().toISOString();
    await this.scent_db.set(key, session);
    return { success: true, elapsed_minutes: state.elapsed_minutes };
  },
});

