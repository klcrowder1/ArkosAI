import Heading from "@/components/ui/heading";
import { Label } from "@/components/ui/label";
import { useCallback, useContext, useEffect, useState } from "react";
import { Toaster } from "sonner";
import { Separator } from "../../components/ui/separator";
import ActivityIndicator from "@/components/indicators/activity-indicator";
import { toast } from "sonner";
import useSWR from "swr";
import axios from "axios";
import { FrigateConfig } from "@/types/frigateConfig";
import { CheckCircle2, XCircle } from "lucide-react";
import { Trans, useTranslation } from "react-i18next";
import { IoIosWarning } from "react-icons/io";
import { Button } from "@/components/ui/button";
import { Link } from "react-router-dom";
import { LuExternalLink } from "react-icons/lu";
import { StatusBarMessagesContext } from "@/context/statusbar-provider";
import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectTrigger,
} from "@/components/ui/select";

type ArkosPlusModel = {
  id: string;
  type: string;
  name: string;
  isBaseModel: boolean;
  supportedDetectors: string[];
  trainDate: string;
  baseModel: string;
  width: number;
  height: number;
};

type ArkosPlusSettings = {
  model: {
    id?: string;
  };
};

type ArkosSettingsViewProps = {
  setUnsavedChanges: React.Dispatch<React.SetStateAction<boolean>>;
};

export default function ArkosPlusSettingsView({
  setUnsavedChanges,
}: ArkosSettingsViewProps) {
  const { t } = useTranslation("views/settings");
  const { data: config, mutate: updateConfig } =
    useSWR<FrigateConfig>("config");
  const [changedValue, setChangedValue] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  const { addMessage, removeMessage } = useContext(StatusBarMessagesContext)!;

  const [arkosPlusSettings, setArkosPlusSettings] =
    useState<ArkosPlusSettings>({
      model: {
        id: undefined,
      },
    });

  const [origPlusSettings, setOrigPlusSettings] = useState<ArkosPlusSettings>(
    {
      model: {
        id: undefined,
      },
    },
  );

  const { data: availableModels = {} } = useSWR<
    Record<string, ArkosPlusModel>
  >("/plus/models", {
    fallbackData: {},
    fetcher: async (url) => {
      const res = await axios.get(url, { withCredentials: true });
      return res.data.reduce(
        (obj: Record<string, ArkosPlusModel>, model: ArkosPlusModel) => {
          obj[model.id] = model;
          return obj;
        },
        {},
      );
    },
  });

  useEffect(() => {
    if (config) {
      if (arkosPlusSettings?.model.id == undefined) {
        setArkosPlusSettings({
          model: {
            id: config.model.plus?.id,
          },
        });
      }

      setOrigPlusSettings({
        model: {
          id: config.model.plus?.id,
        },
      });
    }
    // we know that these deps are correct
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [config]);

  const handleArkosPlusConfigChange = (
    newConfig: Partial<ArkosPlusSettings>,
  ) => {
    setArkosPlusSettings((prevConfig) => ({
      model: {
        ...prevConfig.model,
        ...newConfig.model,
      },
    }));
    setUnsavedChanges(true);
    setChangedValue(true);
  };

  const saveToConfig = useCallback(async () => {
    setIsLoading(true);

    axios
      .put(`config/set?model.path=plus://${arkosPlusSettings.model.id}`, {
        requires_restart: 0,
      })
      .then((res) => {
        if (res.status === 200) {
          toast.success(t("arkosPlus.toast.success"), {
            position: "top-center",
          });
          setChangedValue(false);
          updateConfig();
        } else {
          toast.error(
            t("arkosPlus.toast.error", { errorMessage: res.statusText }),
            {
              position: "top-center",
            },
          );
        }
      })
      .catch((error) => {
        const errorMessage =
          error.response?.data?.message ||
          error.response?.data?.detail ||
          "Unknown error";
        toast.error(
          t("toast.save.error.title", { errorMessage, ns: "common" }),
          {
            position: "top-center",
          },
        );
      })
      .finally(() => {
        addMessage(
          "plus_restart",
          t("arkosPlus.restart_required"),
          undefined,
          "plus_restart",
        );
        setIsLoading(false);
      });
  }, [updateConfig, addMessage, arkosPlusSettings, t]);

  const onCancel = useCallback(() => {
    setArkosPlusSettings(origPlusSettings);
    setChangedValue(false);
    removeMessage("plus_settings", "plus_settings");
  }, [origPlusSettings, removeMessage]);

  useEffect(() => {
    if (changedValue) {
      addMessage(
        "plus_settings",
        `Unsaved Arkos+ settings changes`,
        undefined,
        "plus_settings",
      );
    } else {
      removeMessage("plus_settings", "plus_settings");
    }
    // we know that these deps are correct
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [changedValue]);

  useEffect(() => {
    document.title = t("documentTitle.arkosPlus");
  }, [t]);

  const needCleanSnapshots = () => {
    if (!config) {
      return false;
    }
    return Object.values(config.cameras).some(
      (camera) => camera.snapshots.enabled && !camera.snapshots.clean_copy,
    );
  };

  if (!config) {
    return <ActivityIndicator />;
  }

  return (
    <>
      <div className="flex size-full flex-col md:flex-row">
        <Toaster position="top-center" closeButton={true} />
        <div className="scrollbar-container order-last mb-10 mt-2 flex h-full w-full flex-col overflow-y-auto rounded-lg border-[1px] border-secondary-foreground bg-background_alt p-2 md:order-none md:mb-0 md:mr-2 md:mt-0">
          <Heading as="h3" className="my-2">
            {t("arkosPlus.title")}
          </Heading>

          <Separator className="my-2 flex bg-secondary" />

          <Heading as="h4" className="my-2">
            {t("arkosPlus.apiKey.title")}
          </Heading>

          <div className="mt-2 space-y-6">
            <div className="space-y-3">
              <div className="flex items-center gap-2">
                {config?.plus?.enabled ? (
                  <CheckCircle2 className="h-5 w-5 text-green-500" />
                ) : (
                  <XCircle className="h-5 w-5 text-red-500" />
                )}
                <Label>
                  {config?.plus?.enabled
                    ? t("arkosPlus.apiKey.validated")
                    : t("arkosPlus.apiKey.notValidated")}
                </Label>
              </div>
              <div className="my-2 max-w-5xl text-sm text-muted-foreground">
                <p>{t("arkosPlus.apiKey.desc")}</p>
                {!config?.model.plus && (
                  <>
                    <div className="mt-2 flex items-center text-primary-variant">
                      <Link
                        to="https://arkos.ai/plus"
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline"
                      >
                        {t("arkosPlus.apiKey.plusLink")}
                        <LuExternalLink className="ml-2 inline-flex size-3" />
                      </Link>
                    </div>
                  </>
                )}
              </div>
            </div>

            {config?.model.plus && (
              <>
                <Separator className="my-2 flex bg-secondary" />
                <div className="mt-2 max-w-2xl">
                  <Heading as="h4" className="my-2">
                    {t("arkosPlus.modelInfo.title")}
                  </Heading>
                  <div className="mt-2 space-y-3">
                    {!config?.model?.plus && (
                      <p className="text-muted-foreground">
                        {t("arkosPlus.modelInfo.loading")}
                      </p>
                    )}
                    {config?.model?.plus === null && (
                      <p className="text-danger">
                        {t("arkosPlus.modelInfo.error")}
                      </p>
                    )}
                    {config?.model?.plus && (
                      <div className="grid grid-cols-2 gap-4">
                        <div>
                          <Label className="text-muted-foreground">
                            {t("arkosPlus.modelInfo.baseModel")}
                          </Label>
                          <p>
                            {config.model.plus.baseModel} (
                            {config.model.plus.isBaseModel
                              ? t(
                                  "arkosPlus.modelInfo.plusModelType.baseModel",
                                )
                              : t(
                                  "arkosPlus.modelInfo.plusModelType.userModel",
                                )}
                            )
                          </p>
                        </div>
                        <div>
                          <Label className="text-muted-foreground">
                            {t("arkosPlus.modelInfo.trainDate")}
                          </Label>
                          <p>
                            {new Date(
                              config.model.plus.trainDate,
                            ).toLocaleString()}
                          </p>
                        </div>
                        <div>
                          <Label className="text-muted-foreground">
                            {t("arkosPlus.modelInfo.modelType")}
                          </Label>
                          <p>
                            {config.model.plus.name} (
                            {config.model.plus.width +
                              "x" +
                              config.model.plus.height}
                            )
                          </p>
                        </div>
                        <div>
                          <Label className="text-muted-foreground">
                            {t("arkosPlus.modelInfo.supportedDetectors")}
                          </Label>
                          <p>
                            {config.model.plus.supportedDetectors.join(", ")}
                          </p>
                        </div>
                        <div className="col-span-2">
                          <div className="space-y-2">
                            <div className="text-md">
                              {t("arkosPlus.modelInfo.availableModels")}
                            </div>
                            <div className="space-y-3 text-sm text-muted-foreground">
                              <p>
                                <Trans ns="views/settings">
                                  arkosPlus.modelInfo.modelSelect
                                </Trans>
                              </p>
                            </div>
                          </div>
                          <Select
                            value={arkosPlusSettings.model.id}
                            onValueChange={(value) =>
                              handleArkosPlusConfigChange({
                                model: { id: value as string },
                              })
                            }
                          >
                            {arkosPlusSettings.model.id &&
                            availableModels?.[arkosPlusSettings.model.id] ? (
                              <SelectTrigger>
                                {new Date(
                                  availableModels[
                                    arkosPlusSettings.model.id
                                  ].trainDate,
                                ).toLocaleString() +
                                  " " +
                                  availableModels[arkosPlusSettings.model.id]
                                    .baseModel +
                                  " (" +
                                  (availableModels[arkosPlusSettings.model.id]
                                    .isBaseModel
                                    ? t(
                                        "arkosPlus.modelInfo.plusModelType.baseModel",
                                      )
                                    : t(
                                        "arkosPlus.modelInfo.plusModelType.userModel",
                                      )) +
                                  ") " +
                                  availableModels[arkosPlusSettings.model.id]
                                    .name +
                                  " (" +
                                  availableModels[arkosPlusSettings.model.id]
                                    .width +
                                  "x" +
                                  availableModels[arkosPlusSettings.model.id]
                                    .height +
                                  ")"}
                              </SelectTrigger>
                            ) : (
                              <SelectTrigger>
                                {t(
                                  "arkosPlus.modelInfo.loadingAvailableModels",
                                )}
                              </SelectTrigger>
                            )}

                            <SelectContent>
                              <SelectGroup>
                                {Object.entries(availableModels || {}).map(
                                  ([id, model]) => (
                                    <SelectItem
                                      key={id}
                                      className="cursor-pointer"
                                      value={id}
                                      disabled={
                                        model.type != config.model.model_type ||
                                        !model.supportedDetectors.includes(
                                          Object.values(config.detectors)[0]
                                            .type,
                                        )
                                      }
                                    >
                                      {new Date(
                                        model.trainDate,
                                      ).toLocaleString()}{" "}
                                      <div>
                                        {model.baseModel} {" ("}
                                        {model.isBaseModel
                                          ? t(
                                              "arkosPlus.modelInfo.plusModelType.baseModel",
                                            )
                                          : t(
                                              "arkosPlus.modelInfo.plusModelType.userModel",
                                            )}
                                        {")"}
                                      </div>
                                      <div>
                                        {model.name} (
                                        {model.width + "x" + model.height})
                                      </div>
                                      <div>
                                        {t(
                                          "arkosPlus.modelInfo.supportedDetectors",
                                        )}
                                        : {model.supportedDetectors.join(", ")}
                                      </div>
                                      <div className="text-xs text-muted-foreground">
                                        {id}
                                      </div>
                                    </SelectItem>
                                  ),
                                )}
                              </SelectGroup>
                            </SelectContent>
                          </Select>
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              </>
            )}

            <Separator className="my-2 flex bg-secondary" />

            <div className="mt-2 max-w-5xl">
              <Heading as="h4" className="my-2">
                {t("arkosPlus.snapshotConfig.title")}
              </Heading>
              <div className="mt-2 space-y-3">
                <div className="my-2 text-sm text-muted-foreground">
                  <p>
                    <Trans ns="views/settings">
                      arkosPlus.snapshotConfig.desc
                    </Trans>
                  </p>
                  <div className="mt-2 flex items-center text-primary-variant">
                    <Link
                      to="https://docs.arkos.ai/configuration/plus/faq"
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline"
                    >
                      {t("arkosPlus.snapshotConfig.documentation")}
                      <LuExternalLink className="ml-2 inline-flex size-3" />
                    </Link>
                  </div>
                </div>
                {config && (
                  <div className="overflow-x-auto">
                    <table className="max-w-2xl text-sm">
                      <thead>
                        <tr className="border-b border-secondary">
                          <th className="px-4 py-2 text-left">
                            {t("arkosPlus.snapshotConfig.table.camera")}
                          </th>
                          <th className="px-4 py-2 text-center">
                            {t("arkosPlus.snapshotConfig.table.snapshots")}
                          </th>
                          <th className="px-4 py-2 text-center">
                            <Trans ns="views/settings">
                              arkosPlus.snapshotConfig.table.cleanCopySnapshots
                            </Trans>
                          </th>
                        </tr>
                      </thead>
                      <tbody>
                        {Object.entries(config.cameras).map(
                          ([name, camera]) => (
                            <tr
                              key={name}
                              className="border-b border-secondary"
                            >
                              <td className="px-4 py-2">{name}</td>
                              <td className="px-4 py-2 text-center">
                                {camera.snapshots.enabled ? (
                                  <CheckCircle2 className="mx-auto size-5 text-green-500" />
                                ) : (
                                  <XCircle className="mx-auto size-5 text-danger" />
                                )}
                              </td>
                              <td className="px-4 py-2 text-center">
                                {camera.snapshots?.enabled &&
                                camera.snapshots?.clean_copy ? (
                                  <CheckCircle2 className="mx-auto size-5 text-green-500" />
                                ) : (
                                  <XCircle className="mx-auto size-5 text-danger" />
                                )}
                              </td>
                            </tr>
                          ),
                        )}
                      </tbody>
                    </table>
                  </div>
                )}
                {needCleanSnapshots() && (
                  <div className="mt-2 max-w-xl rounded-lg border border-secondary-foreground bg-secondary p-4 text-sm text-danger">
                    <div className="flex items-center gap-2">
                      <IoIosWarning className="mr-2 size-5 text-danger" />
                      <div className="max-w-[85%] text-sm">
                        <Trans ns="views/settings">
                          arkosPlus.snapshotConfig.cleanCopyWarning
                        </Trans>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </div>

            <Separator className="my-2 flex bg-secondary" />

            <div className="flex w-full flex-row items-center gap-2 pt-2 md:w-[25%]">
              <Button
                className="flex flex-1"
                aria-label={t("button.reset", { ns: "common" })}
                onClick={onCancel}
              >
                {t("button.reset", { ns: "common" })}
              </Button>
              <Button
                variant="select"
                disabled={!changedValue || isLoading}
                className="flex flex-1"
                aria-label="Save"
                onClick={saveToConfig}
              >
                {isLoading ? (
                  <div className="flex flex-row items-center gap-2">
                    <ActivityIndicator />
                    <span>{t("button.saving", { ns: "common" })}</span>
                  </div>
                ) : (
                  t("button.save", { ns: "common" })
                )}
              </Button>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}
