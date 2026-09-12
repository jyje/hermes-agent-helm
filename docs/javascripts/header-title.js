// Material's header shows two texts inside `.md-header__title`: the site
// name (always present) and a second, scroll-revealed "topic" span that
// mirrors `page.title`. On the localized homepages `page.title` comes
// from the nav config's localized home label, not the site name, so the
// header text visibly changed once the user scrolled past the page's own
// heading. header.html renders that span unconditionally, with no per-role
// override, and `page.title` also drives the nav label and the <title>
// tag - both of which should stay as the short localized home text - so this
// is patched here instead of via frontmatter/nav config, on the homepage
// only, leaving every other page's header topic untouched.
document$.subscribe(function () {
  if (!/^\/hermes-agent-helm\/((ko|ja|zh)\/)?$/.test(location.pathname)) {
    return;
  }
  var siteName = document.querySelector(
    ".md-header__topic:not([data-md-component]) .md-ellipsis"
  );
  var topic = document.querySelector(
    '[data-md-component="header-topic"] .md-ellipsis'
  );
  if (siteName && topic) {
    topic.textContent = siteName.textContent.trim();
  }
});
