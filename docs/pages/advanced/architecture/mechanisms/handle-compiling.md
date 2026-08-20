# Handle Compiling

`Magewirephp\Magewire\Mechanisms\HandleCompiling\HandleCompiling` owns Magewire's template compilation pipeline. It runs at mechanism priority `1500`, after frontend assets have been registered.

The mechanism:

- discovers and registers template directive scopes;
- compiles Magewire directives and echo expressions in `.phtml` files;
- stores compiled views below `var/magewire/views/{area}/`;
- recompiles a view when its source changes.

Compiler classes moved from `Features\SupportMagewireCompiling` to `Mechanisms\HandleCompiling` in Magewire 3.3. Extensions using the old namespace must update their imports.

## Clear compiled views

Clear all compiled Magewire views after changing directives or when diagnosing stale output:

```shell
bin/magento magewire:compile:clear
```

Limit the command to one Magento area when appropriate:

```shell
bin/magento magewire:compile:clear --area frontend
bin/magento magewire:compile:clear -a adminhtml
```

See [Template Directives](../../../features/magewire-template-directives.md) for the template-facing syntax.
