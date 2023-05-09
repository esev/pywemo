// Replace ${VARIABLES} in the RELEASE_NOTES_TEMPLATE.md file.
// Used by .github/workflows/publish.yml.
const fsp = require('fs').promises;

module.exports = async ({github, context, process}) => {
    const fileOpts = { encoding: 'utf8' };
    let template = await fsp.readFile(process.env.TEMPLATE_FILE, fileOpts);
    for (const [key, value] of Object.entries(process.env)) {
        template = template.replaceAll(`\${${key}}`, value);
    }

    let hashes = await fsp.readFile(process.env.SHA256SUM_TXT, fileOpts);
    hashes = hashes.trim()
    template = template.replace('${SHA256SUM}', hashes);

    const release = await github.rest.repos.getReleaseByTag({
        ...context.repo,
        tag: process.env.GITHUB_REF_NAME,
    });
    const body = (release.body || '').trim();

    if (body.includes(hashes)) {
        throw new Error('The release template has already been applied.');
    }

    return await github.rest.repos.updateRelease({
        ...context.repo,
        release_id: release.id,
        body: template.replace('${BODY}', body),
    });
}
