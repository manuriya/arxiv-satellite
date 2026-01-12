class BlockCreator:
    def __call__(self, article: dict[str, str]) -> dict:
        blocks = [
            dict(type="divider"),
            self._set_header(article["title"]),
            self._set_url(article["title_link"]),
            self._set_tags(article["description"]),
            self._set_description(article["description"]),
        ]
        return blocks

    @staticmethod
    def _set_header(header: str) -> dict:
        return dict(type="header", text=dict(type="plain_text", text=header))

    @staticmethod
    def _set_url(url: str) -> dict:
        return dict(
            type="rich_text",
            elements=[
                dict(
                    type="rich_text_section",
                    elements=[dict(type="link", url=url), dict(type="text", text="\n")],
                ),
            ],
        )

    @staticmethod
    def _set_tags(description: str) -> dict:
        tag_text = [
            s
            for s in description.split("\n\n")[-1].replace(" ", "").split("#")
            if len(s) > 0
        ]

        elements = [
            dict(type="text", text="#", style=dict(italic=True, code=True)),
        ] + sum(
            [
                [
                    dict(type="text", text=tag, style=dict(italic=True, code=True)),
                    dict(type="text", text=" "),
                    dict(type="text", text="#", style=dict(italic=True, code=True)),
                ]
                for tag in tag_text
            ],
            [],
        )[:-1]
        return dict(
            type="rich_text",
            elements=[dict(type="rich_text_section", elements=elements)],
        )

    @staticmethod
    def _set_description(description: str) -> dict:
        description_items = [
            dict(title=s.split("\n")[0], text="\n".join(s.split("\n")[1:]))
            for s in description.split("\n\n")[:-1]
        ]
        elements = [
            dict(
                type="rich_text_section",
                elements=[
                    dict(
                        type="text",
                        text=f"{description['title']}\n",
                        style=dict(bold=True),
                    ),
                    dict(
                        type="text",
                        text=f"{description['text']}",
                    ),
                ],
            )
            for description in description_items
        ]
        return dict(type="rich_text", elements=elements)
