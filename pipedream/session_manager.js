export default defineComponent({
  props: { scent_db: { type: "data_store" } },
  async run({ steps, $ }) {
    const body = steps.trigger.event.body || {};
    const action = body.action || "poll";
    const sessionId = body.session_id || "default";
    const key = `session:${sessionId}`;
    const now = new Date();
    let session = await this.scent_db.get(key);

    if (action === "init") {
      session = {
        session_id: sessionId,
        session_started_at: now.toISOString(),
        active: true,
        slots: body.slots || {},
        exclusions: body.exclusions || "None",
        last_song: null,
        last_energy: null,
        last_valence: null,
      };
      await this.scent_db.set(key, session);
    }
    if (action === "end") {
      if (session) {
        session.active = false;
        session.ended_at = now.toISOString();
        await this.scent_db.set(key, session);
      }
      return { continue_processing: false, status: "ended", session_id: sessionId };
    }
    if (!session?.active) {
      return { continue_processing: false, status: "inactive", session_id: sessionId };
    }
    const elapsedSeconds = Math.max(0, Math.floor((now - new Date(session.session_started_at)) / 1000));
    return {
      continue_processing: true,
      session_id: sessionId,
      session_started_at: session.session_started_at,
      elapsed_seconds: elapsedSeconds,
      elapsed_minutes: Math.floor(elapsedSeconds / 60),
      slots: session.slots,
      exclusions: session.exclusions,
      previous_song: session.last_song,
      previous_energy: session.last_energy,
      previous_valence: session.last_valence,
    };
  },
});

